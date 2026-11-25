import hashlib

import pytest
from codepilot.config import Budgets
from codepilot.patching import Edit, Proposal, apply_edits


def proposal(root, **overrides):
    entry = {
        "path": "src/f.py",
        "expected_sha256": hashlib.sha256((root / "src/f.py").read_bytes()).hexdigest(),
        "old": "return x > 18",
        "new": "return x >= 18",
    }
    entry.update(overrides)
    return Proposal(decision="propose", rationale="boundary", edits=[Edit(**entry)])


@pytest.fixture
def base(tmp_path):
    root = tmp_path / "base"
    (root / "src").mkdir(parents=True)
    (root / "src/f.py").write_text("def eligible(x):\n    return x > 18\n")
    return root


def test_valid_candidate_does_not_change_baseline(base, tmp_path):
    result = apply_edits(base, tmp_path / "candidate", proposal(base), Budgets())
    assert result["changed_lines"] == 2
    assert ">= 18" in (tmp_path / "candidate/src/f.py").read_text()
    assert ">= 18" not in (base / "src/f.py").read_text()


@pytest.mark.parametrize(
    "values",
    [
        {"path": "src/../.env"},
        {"path": "tests/check.py"},
        {"expected_sha256": "0" * 64},
        {"old": "not present"},
        {"new": "return !@"},
        {"new": "return x > 18"},
    ],
)
def test_rejects_unsafe_edits(base, tmp_path, values):
    with pytest.raises((ValueError, SyntaxError, FileNotFoundError)):
        apply_edits(base, tmp_path / "candidate", proposal(base, **values), Budgets())
    assert not (tmp_path / "candidate").exists()


def test_ambiguous_and_size(base, tmp_path):
    (base / "src/f.py").write_text("def f(x):\n    return x > 18\ndef g(x):\n    return x > 18\n")
    with pytest.raises(ValueError, match="ambiguous"):
        apply_edits(base, tmp_path / "candidate", proposal(base), Budgets())
