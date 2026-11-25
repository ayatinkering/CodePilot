"""Exact preimage edits to a fresh candidate; original tests cannot be edited."""

import ast
import difflib
import hashlib
import shutil
from pathlib import Path, PurePosixPath
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from codepilot.config import Budgets


class Edit(BaseModel):
    model_config = ConfigDict(extra="forbid")
    path: str
    expected_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    old: str = Field(min_length=1, max_length=20000)
    new: str = Field(max_length=20000)


class Proposal(BaseModel):
    model_config = ConfigDict(extra="forbid")
    decision: Literal["propose", "abstain"]
    rationale: str = Field(max_length=2000)
    edits: list[Edit] = Field(max_length=3)
    generated_test: str = Field(default="", max_length=10000)


def digest(data: bytes):
    return hashlib.sha256(data).hexdigest()


def apply_edits(baseline: Path, candidate: Path, proposal: Proposal, budgets: Budgets):
    if candidate.exists() or proposal.decision != "propose" or not proposal.edits:
        raise ValueError("candidate_must_be_new_with_edits")
    edits = proposal.edits
    if len(edits) > budgets.production_files or len({e.path for e in edits}) != len(edits):
        raise ValueError("file_count_or_duplicate_edit")
    changes, diffs = {}, []
    for edit in edits:
        parts = PurePosixPath(edit.path).parts
        if (
            not parts
            or parts[0] != "src"
            or ".." in parts
            or "\\" in edit.path
            or any(p.startswith(".") for p in parts)
            or not edit.path.endswith(".py")
        ):
            raise ValueError("protected_or_unsafe_path")
        path = baseline / edit.path
        if path.is_symlink() or not path.resolve().is_relative_to(baseline.resolve()):
            raise ValueError("symlink_or_path_escape")
        raw = path.read_bytes()
        if digest(raw) != edit.expected_sha256:
            raise ValueError("preimage_hash_mismatch")
        old = raw.decode("utf-8")
        if old.count(edit.old) != 1 or edit.old == edit.new:
            raise ValueError("ambiguous_or_empty_edit")
        new = old.replace(edit.old, edit.new, 1)
        ast.parse(new)  # Parse only: never execute or import proposed source on host.
        delta = "".join(
            difflib.unified_diff(
                old.splitlines(True),
                new.splitlines(True),
                fromfile="a/" + edit.path,
                tofile="b/" + edit.path,
            )
        )
        diffs.append(delta)
        changes[edit.path] = new
    diff = "".join(diffs)
    changed_lines = sum(
        line.startswith(("+", "-")) and not line.startswith(("+++", "---"))
        for line in diff.splitlines()
    )
    if changed_lines > budgets.changed_lines:
        raise ValueError("changed_line_budget_exceeded")
    if any(p.is_symlink() for p in baseline.rglob("*")):
        raise ValueError("baseline_contains_symlink")
    shutil.copytree(baseline, candidate)
    for name, new in changes.items():
        (candidate / name).write_text(new)
    return {
        "diff": diff,
        "patch_digest": digest(diff.encode()),
        "files": sorted(changes),
        "changed_lines": changed_lines,
    }
