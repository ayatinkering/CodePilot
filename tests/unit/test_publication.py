import json
import shutil

import pytest
from codepilot.config import Budgets, Settings
from codepilot.demo import ROOT
from codepilot.github import publish
from codepilot.jobs import Jobs
from codepilot.patching import apply_edits
from codepilot.pipeline import offline_proposal
from codepilot.storage import Store


@pytest.fixture
def ready(tmp_path):
    settings = Settings(data_dir=tmp_path)
    store = Store(tmp_path / "db")
    store.initialize()
    jobs = Jobs(store)
    run = jobs.submit(
        {"repository_id": "boundary", "mode": "repair"},
        "a" * 40,
        Budgets(),
        {"provider": "offline"},
    )
    for state in [
        "preparing",
        "baselining",
        "indexing",
        "retrieving",
        "planning",
        "generating",
        "validating",
        "ready_for_review",
    ]:
        jobs.transition(run, state)
    root = tmp_path / "runs" / run
    root.mkdir(parents=True)
    shutil.copytree(ROOT / "fixtures/targets/boundary", root / "baseline")
    source = {"src/discounts.py": (root / "baseline/src/discounts.py").read_text()}
    proposal = offline_proposal({"mode": "repair"}, source, 0)
    patch = apply_edits(root / "baseline", root / "candidate-0", proposal, Budgets())
    result = {
        "approved_candidate": 0,
        "patch_digest": patch["patch_digest"],
        "attempts": [
            {
                "attempt": 0,
                "proposal": proposal.model_dump(),
                "existing_tests": {"status": "passed"},
                "evaluator_tests": {"status": "passed"},
            }
        ],
    }
    (root / "result.json").write_text(json.dumps(result))
    (tmp_path / "repositories.json").write_text(
        json.dumps(
            {
                "boundary": {
                    "publication_allowed": True,
                    "github_repo": settings.github_repo,
                    "base_branch": "demo/fixture",
                }
            }
        )
    )
    return jobs, settings, run, root, patch["patch_digest"]


def test_publication_stale_and_changed_candidate(ready, monkeypatch):
    jobs, settings, run, root, digest = ready
    with pytest.raises(ValueError, match="Approval"):
        publish(jobs, settings, run, "b" * 40, digest)
    monkeypatch.setattr("codepilot.github.github", lambda *a, **k: {"object": {"sha": "b" * 40}})
    with pytest.raises(ValueError, match="Remote base changed"):
        publish(jobs, settings, run, "a" * 40, digest)
    (root / "candidate-0/tests/test_discounts.py").write_text("tampered")
    with pytest.raises(ValueError, match="Candidate changed"):
        publish(jobs, settings, run, "a" * 40, digest)
    assert jobs.get(run)["state"] == "ready_for_review"


def test_publication_reconciles_without_duplicate_writes(ready, monkeypatch):
    jobs, settings, run, _root, digest = ready
    calls = []

    def remote(path, method="GET", payload=None):
        calls.append(method)
        if "/git/ref/" in path:
            return {"object": {"sha": "a" * 40}}
        if "/matching-refs/" in path:
            return [{"ref": "refs/heads/codepilot/run-" + run, "object": {"sha": "c" * 40}}]
        if "/commits/" in path:
            return {
                "message": f"CodePilot run {run}; patch {digest}",
                "parents": [{"sha": "a" * 40}],
            }
        if "/pulls?" in path:
            return [{"html_url": "https://github.com/ayatinkering/CodePilot/pull/99", "number": 99}]
        raise AssertionError(path)

    monkeypatch.setattr("codepilot.github.github", remote)
    first = publish(jobs, settings, run, "a" * 40, digest)
    assert publish(jobs, settings, run, "a" * 40, digest) == first
    assert jobs.get(run)["state"] == "published"
    assert set(calls) == {"GET"}
