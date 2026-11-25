"""Read-only first-parent commit analysis; file impact is conservative."""

from pathlib import Path

from codepilot.acquisition import git


def analyze_commit(repository, sha, index):
    repo = Path(repository)
    lineage = git(repo, "rev-list", "--parents", "-n", "1", sha).decode().split()
    parent = lineage[1] if len(lineage) > 1 else None
    args = (
        ("diff", "--name-only", "-z", parent, sha, "--")
        if parent
        else ("diff-tree", "--root", "--no-commit-id", "--name-only", "-r", "-z", sha, "--")
    )
    changed = [p.decode() for p in git(repo, *args).split(b"\0") if p]
    return {
        "base_sha": sha,
        "parent_sha": parent,
        "comparison": "first parent" if parent else "empty tree",
        "changed_files": changed,
        "affected_symbols": [
            {
                "path": f["path"],
                "symbol": s["name"],
                "start_line": s["start_line"],
                "end_line": s["end_line"],
            }
            for f in index["files"]
            if f["path"] in changed
            for s in f["symbols"]
            if s["kind"] in {"function", "method"}
        ],
        "limitation": "Conservative file-level impact, not semantic change or dependency proof.",
    }
