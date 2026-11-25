"""Read Git blobs without checking out hooks, submodules, filters or target code."""

import hashlib
import re
import subprocess
from pathlib import Path, PurePosixPath

from codepilot.config import Budgets


class AcquisitionError(ValueError):
    pass


def git(repo: Path, *args: str) -> bytes:
    result = subprocess.run(
        [
            "git",
            "-c",
            "core.hooksPath=/dev/null",
            "-c",
            "protocol.file.allow=never",
            "-C",
            str(repo),
            *args,
        ],
        check=True,
        capture_output=True,
        timeout=30,
        env={
            "PATH": "/usr/bin:/bin",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": "/dev/null",
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_NO_REPLACE_OBJECTS": "1",
        },
    )
    return result.stdout


EXCLUDED = {".git", ".venv", "node_modules", "__pycache__", ".codepilot", "dist", ".aws", ".ssh"}


def acquire(source: str, allowed: list[Path], destination: Path, budgets: Budgets, ref="HEAD"):
    raw = Path(source)
    if ".." in raw.parts or not raw.is_absolute():
        raise AcquisitionError("Use an absolute allowlisted path without traversal")
    if raw.is_symlink() or raw.resolve() != raw:
        raise AcquisitionError("Symlink paths are not accepted")
    repo = raw.resolve(strict=True)
    if repo not in [p.resolve(strict=True) for p in allowed]:
        raise AcquisitionError("Repository is not allowlisted")
    if not re.fullmatch(r"[0-9a-f]{40}", ref) and ref != "HEAD":
        raise AcquisitionError("Use HEAD or a full commit SHA")
    sha = git(repo, "rev-parse", "--verify", f"{ref}^{{commit}}").decode().strip()
    if destination.exists():
        raise AcquisitionError("Snapshot destination must be new")
    records = git(repo, "ls-tree", "-r", "-z", sha).split(b"\0")
    selected, skipped, total = [], [], 0
    for record in records:
        if not record:
            continue
        metadata, rawpath = record.split(b"\t", 1)
        mode, kind, oid = metadata.decode().split()
        path = rawpath.decode("utf-8", errors="strict")
        parts = PurePosixPath(path).parts
        reason = None
        if path.startswith("/") or ".." in parts or "\\" in path:
            raise AcquisitionError("Unsafe Git path")
        if mode not in ("100644", "100755") or kind != "blob":
            reason = "symlink_or_submodule"
        elif any(p in EXCLUDED or p.startswith(".env") for p in parts) or path.endswith(
            (".pem", ".key")
        ):
            reason = "excluded_or_sensitive"
        size = int(git(repo, "cat-file", "-s", oid)) if reason is None else 0
        if size > budgets.file_bytes:
            reason = "file_limit"
        if reason:
            skipped.append({"path": path, "reason": reason})
            continue
        data = git(repo, "cat-file", "blob", oid)
        if b"\0" in data:
            skipped.append({"path": path, "reason": "binary"})
            continue
        total += len(data)
        if total > budgets.indexed_bytes or len(selected) >= budgets.indexed_files:
            raise AcquisitionError("Repository size limit exceeded")
        selected.append((path, data))
    destination.mkdir(parents=True)
    files = []
    for name, data in selected:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        files.append({"path": name, "sha256": hashlib.sha256(data).hexdigest()})
    return {"base_sha": sha, "files": files, "skipped": skipped}
