from pathlib import Path

from codepilot.acquisition import git
from codepilot.analysis import analyze_commit
from codepilot.demo import prepare_demo
from codepilot.indexing import parse_source


def test_root_commit_has_real_changed_files_and_symbols(tmp_path):
    entry = prepare_demo(tmp_path)["refactor"]
    repo = Path(entry["path"])
    sha = git(repo, "rev-parse", "HEAD").decode().strip()
    parsed = parse_source((repo / "src/orders.py").read_bytes(), "src/orders.py", sha)
    result = analyze_commit(repo, sha, {"files": [parsed]})
    assert result["parent_sha"] is None
    assert "src/orders.py" in result["changed_files"]
    assert any(s["symbol"].endswith(".total_order") for s in result["affected_symbols"])
