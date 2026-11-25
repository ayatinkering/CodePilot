"""A separate trusted worker process; no background request tasks."""

import fcntl
import json
import os
import subprocess
import time
from contextlib import contextmanager
from pathlib import Path

from codepilot.acquisition import acquire
from codepilot.config import Budgets, Settings
from codepilot.jobs import Jobs
from codepilot.runner import run_tests
from codepilot.storage import Store


@contextmanager
def worker_lock(directory: Path):
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / "worker.lock").open("w") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError("A worker already owns this data directory") from exc
        yield


def execute_one(jobs: Jobs, settings: Settings, allowed: list[Path], image: str):
    run_id = jobs.claim()
    if run_id is None:
        return False
    run = jobs.get(run_id)
    task = json.loads(run["task_json"])
    budgets = Budgets.model_validate_json(run["budgets_json"])
    directory = settings.data_dir / "runs" / run_id
    directory.mkdir(parents=True)
    cancelled = lambda: jobs.get(run_id)["state"] == "cancelled"
    try:
        manifest = acquire(
            task["repository"], allowed, directory / "baseline", budgets, run["base_sha"]
        )
        (directory / "snapshot.json").write_text(json.dumps(manifest, indent=2))
        if cancelled():
            return True
        jobs.transition(run_id, "baselining")
        result = run_tests(directory / "baseline", image, budgets.test_seconds, cancelled)
        (directory / "baseline-report.json").write_text(json.dumps(result, indent=2))
        if not cancelled():
            if result["status"] == "passed":
                jobs.transition(run_id, "abstained", "pipeline_not_implemented_after_baseline")
            else:
                jobs.transition(run_id, "failed", result["status"])
    except (OSError, ValueError, KeyError, subprocess.SubprocessError):
        # No arbitrary exception/target text is copied into persisted public events.
        if not cancelled():
            jobs.transition(run_id, "failed", "preparation_or_runner_error")
    return True


def main():
    settings = Settings()
    store = Store(settings.data_dir / "codepilot.sqlite3")
    store.initialize()
    jobs = Jobs(store)
    # Operator-owned configuration; task text cannot authorize a repository.
    allowed = [
        Path(p) for p in os.environ.get("CODEPILOT_ALLOWED_REPOS", "").split(os.pathsep) if p
    ]
    image = os.environ.get("CODEPILOT_RUNNER_IMAGE", "")
    with worker_lock(settings.data_dir):
        jobs.recover()
        while True:
            if not execute_one(jobs, settings, allowed, image):
                time.sleep(0.5)


if __name__ == "__main__":
    main()
