"""Reproducible offline acceptance cases, not an AI success-rate benchmark."""

import csv
import json
import time

from codepilot.acquisition import git
from codepilot.config import Budgets
from codepilot.demo import prepare_demo
from codepilot.jobs import Jobs
from codepilot.storage import Store
from codepilot.worker import execute_one, worker_lock

CASES = [
    ("repair-A", "boundary", "normal", "A", "ready_for_review"),
    ("repair-B", "boundary", "normal", "B", "ready_for_review"),
    ("repair-C", "boundary", "normal", "C", "ready_for_review"),
    ("repair-second", "boundary", "repair_second", "C", "ready_for_review"),
    ("repair-wrong", "boundary", "wrong", "C", "abstained"),
    ("repair-illegal", "boundary", "illegal", "C", "abstained"),
    ("repair-unsupported", "boundary", "unsupported", "C", "abstained"),
    ("refactor-preserved", "refactor", "normal", "C", "ready_for_review"),
    ("refactor-regression", "refactor", "wrong", "C", "abstained"),
    ("original-failure", "baseline_failed", "normal", "C", "failed"),
    ("missing-dependency", "missing_dependency", "normal", "C", "failed"),
    ("zero-tests", "zero_tests", "normal", "C", "failed"),
]


def evaluate(settings, output):
    from pathlib import Path

    entries = prepare_demo(settings.data_dir)
    store = Store(settings.data_dir / "codepilot.sqlite3")
    store.initialize()
    jobs = Jobs(store)
    rows = []
    with worker_lock(settings.data_dir):
        jobs.recover()
        for name, repository, scenario, variant, expected in CASES:
            entry = entries[repository]
            sha = git(Path(entry["path"]), "rev-parse", "HEAD").decode().strip()
            run_id = jobs.submit(
                {
                    "repository": entry["path"],
                    "repository_id": repository,
                    "text": entry["task"],
                    "mode": entry["mode"],
                    "scenario": scenario,
                    "variant": variant,
                },
                sha,
                Budgets(candidates=2),
                {"provider": "offline", "model": "scripted-demo"},
            )
            started = time.monotonic()
            while jobs.get(run_id)["state"] == "queued":
                execute_one(
                    jobs,
                    settings,
                    [Path(e["path"]) for e in entries.values()],
                    settings.runner_image,
                )
            run = jobs.get(run_id)
            root = settings.data_dir / "runs" / run_id
            result = (
                json.loads((root / "result.json").read_text())
                if (root / "result.json").exists()
                else {}
            )
            baseline = json.loads((root / "baseline-report.json").read_text())
            row = {
                "case": name,
                "run_id": run_id,
                "base_sha": sha,
                "variant": variant,
                "expected": expected,
                "actual": run["state"],
                "passed": expected == run["state"],
                "reason": run["terminal_reason"],
                "attempts": len(result.get("attempts", [])),
                "seconds": round(time.monotonic() - started, 3),
                "generation_tokens": 0,
                "baseline": baseline,
                "result": result,
            }
            rows.append(row)
            print(f"{name}: {run['state']} (expected {expected})", flush=True)
    output.mkdir(parents=True, exist_ok=True)
    report = {
        "scope": "12 offline acceptance scenarios over two synthetic source fixtures; not model quality",
        "live_generation": False,
        "runner_image": settings.runner_image,
        "cases": rows,
        "passed": sum(r["passed"] for r in rows),
        "total": len(rows),
    }
    (output / "results.json").write_text(json.dumps(report, indent=2))
    columns = [
        "case",
        "run_id",
        "base_sha",
        "variant",
        "expected",
        "actual",
        "passed",
        "reason",
        "attempts",
        "seconds",
        "generation_tokens",
    ]
    with (output / "results.csv").open("w") as handle:
        writer = csv.DictWriter(handle, columns, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    (output / "summary.md").write_text(
        f"# Offline acceptance results\n\n{report['passed']}/{report['total']} expected outcomes. "
        "These are scripted acceptance scenarios, not an AI repair benchmark. A/B/C vary retrieval only; "
        "the scripted proposal is the same, so this cannot measure retrieval impact on model quality.\n\n"
        "Raw JSON includes test outcomes, candidate diffs, timings, provenance, and rejection reasons. "
        "Generated tests are auxiliary; protected evaluator tests determine acceptance.\n"
    )
    return report
