"""Deterministic integration of live-provider routing; no network in unit tests."""

import hashlib
import json
import shutil

import pytest
from codepilot import pipeline
from codepilot.config import Budgets, Settings
from codepilot.demo import ROOT
from codepilot.jobs import Jobs
from codepilot.providers import Plan, ProviderFailure, Reply
from codepilot.storage import Store


@pytest.fixture
def harness(tmp_path, monkeypatch):
    settings = Settings(data_dir=tmp_path, GEMINI_API_KEY="test-not-real", model="gemini-test")
    store = Store(tmp_path / "db")
    store.initialize()
    jobs = Jobs(store)
    run = jobs.submit(
        {
            "repository": "unused",
            "repository_id": "boundary",
            "text": "Include age 18",
            "mode": "repair",
        },
        "a" * 40,
        Budgets(generation_calls=2),
        {"provider": "gemini", "model": "gemini-test"},
    )
    for state in ["preparing", "baselining"]:
        jobs.transition(run, state)
    directory = tmp_path / "runs" / run
    directory.mkdir(parents=True)
    shutil.copytree(ROOT / "fixtures/targets/boundary", directory / "baseline")
    manifest = {
        "base_sha": "a" * 40,
        "files": [
            {
                "path": p.relative_to(directory / "baseline").as_posix(),
                "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            }
            for p in (directory / "baseline").rglob("*.py")
        ],
    }
    monkeypatch.setattr(pipeline, "analyze_commit", lambda *a: {})
    monkeypatch.setattr(pipeline, "Embedder", lambda *a: object())
    monkeypatch.setattr(
        pipeline, "build_index", lambda *a: {"model": "test-embedding", "cache_hits": 0}
    )
    monkeypatch.setattr(
        pipeline,
        "search",
        lambda *a, **k: [{"id": "one", "path": "src/discounts.py", "text": "return age > 18"}],
    )
    monkeypatch.setattr(pipeline, "registry", lambda *a: {"boundary": {"evaluator": "boundary"}})
    monkeypatch.setattr(
        pipeline, "offline_proposal", lambda *a: pytest.fail("Live run called scripted fallback")
    )
    monkeypatch.setattr(
        pipeline,
        "run_tests",
        lambda path, *a: {
            "status": "baseline_failed"
            if path.name in {"evaluator-baseline", "generated-baseline-0"}
            else "passed"
        },
    )
    return settings, jobs, run, directory, manifest


def test_live_plan_and_proposal_use_exact_call_budget_without_evaluator_leak(harness, monkeypatch):
    settings, jobs, run, root, manifest = harness
    prompts = []

    class FakeGemini:
        def __init__(self, *a, schema=Plan, **k):
            self.schema = schema

        def close(self):
            pass

        def generate(self, contents, max_output_tokens):
            prompts.append(contents)
            if self.schema is Plan:
                text = json.dumps(
                    {
                        "decision": "propose",
                        "rationale": "Fix boundary",
                        "steps": ["Edit comparison"],
                        "evidence_ids": ["one"],
                        "proposed_files": ["src/discounts.py"],
                        "acceptance_criteria": ["Age 18 qualifies"],
                        "risks": [],
                    }
                )
            else:
                source = (root / "baseline/src/discounts.py").read_bytes()
                text = json.dumps(
                    {
                        "decision": "propose",
                        "rationale": "Include exact boundary",
                        "edits": [
                            {
                                "path": "src/discounts.py",
                                "expected_sha256": hashlib.sha256(source).hexdigest(),
                                "old": "return age > 18",
                                "new": "return age >= 18",
                            }
                        ],
                    }
                )
            return Reply(text, 100, "gemini-test", "live")

    monkeypatch.setattr(pipeline, "GeminiProvider", FakeGemini)
    pipeline.execute_pipeline(jobs, settings, run, root, manifest, "unused")
    assert jobs.get(run)["state"] == "ready_for_review"
    result = json.loads((root / "result.json").read_text())
    assert result["provider"]["calls"] == 2 and result["provider"]["tokens"] == 200
    assert len(prompts) == 2
    assert all(
        "range(0, 100)" not in p and "test_exact_boundary_and_neighbors" not in p for p in prompts
    )


def test_live_outage_persists_attempt_usage_and_never_falls_back(harness, monkeypatch):
    settings, jobs, run, root, manifest = harness

    class Unavailable:
        def __init__(self, *a, **k):
            pass

        def close(self):
            pass

        def generate(self, *a):
            raise ProviderFailure("gemini_service_unavailable")

    monkeypatch.setattr(pipeline, "GeminiProvider", Unavailable)
    pipeline.execute_pipeline(jobs, settings, run, root, manifest, "unused")
    result = json.loads((root / "result.json").read_text())
    assert jobs.get(run)["terminal_reason"] == "gemini_service_unavailable"
    assert result["provider"]["calls"] == 1
    assert result["provider"]["tokens"] > 0 and result["provider"]["usage_known"] is False
    assert result["attempts"] == []
