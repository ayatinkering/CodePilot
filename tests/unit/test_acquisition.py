import subprocess

import pytest
from codepilot.acquisition import AcquisitionError, acquire
from codepilot.config import Budgets


def command(path, *args):
    return subprocess.run(["git", "-C", str(path), *args], check=True, capture_output=True).stdout


@pytest.fixture
def repo(tmp_path):
    repo = tmp_path / "source"
    repo.mkdir()
    command(repo, "init")
    command(repo, "config", "user.name", "Fixture")
    command(repo, "config", "user.email", "fixture@example.invalid")
    (repo / "sample.py").write_text("def value(): return 1\n")
    (repo / ".env").write_text("NOT_A_REAL_SECRET=fixture\n")
    (repo / "escape.py").symlink_to("/etc/passwd")
    command(repo, "add", "sample.py", ".env", "escape.py")
    command(repo, "commit", "-m", "fixture")
    return repo


def test_exact_snapshot_and_original_unchanged(repo, tmp_path):
    sha = command(repo, "rev-parse", "HEAD").decode().strip()
    (repo / "sample.py").write_text("uncommitted work stays here\n")
    before = command(repo, "status", "--porcelain")
    result = acquire(str(repo), [repo], tmp_path / "snapshot", Budgets(), sha)
    assert result["base_sha"] == sha
    assert (tmp_path / "snapshot/sample.py").read_text() == "def value(): return 1\n"
    assert not (tmp_path / "snapshot/.env").exists()
    assert not (tmp_path / "snapshot/escape.py").exists()
    assert len(result["skipped"]) == 2
    assert command(repo, "status", "--porcelain") == before
    assert (repo / "sample.py").read_text() == "uncommitted work stays here\n"


def test_policy_rejects_unknown_and_traversal(repo, tmp_path):
    for source, allow in [(str(repo), []), (str(repo / "../source"), [repo])]:
        with pytest.raises(AcquisitionError):
            acquire(source, allow, tmp_path / "snapshot", Budgets())


def test_size_exclusion(repo, tmp_path):
    result = acquire(str(repo), [repo], tmp_path / "snapshot", Budgets(file_bytes=1))
    assert not result["files"]
    assert any(s["reason"] == "file_limit" for s in result["skipped"])
