from concurrent.futures import ThreadPoolExecutor

import pytest
from codepilot.config import Budgets
from codepilot.jobs import Jobs
from codepilot.storage import Store
from codepilot.worker import worker_lock


@pytest.fixture
def jobs(tmp_path):
    store = Store(tmp_path / "db")
    store.initialize()
    return Jobs(store)


def submit(jobs):
    return jobs.submit({"text": "fix boundary"}, "a" * 40, Budgets(), {"mode": "offline"})


def test_claim_concurrency_and_atomic_events(jobs):
    run = submit(jobs)
    submit(jobs)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: jobs.claim(), range(2)))
    assert results.count(run) == 1
    assert results.count(None) == 1
    assert [e["sequence"] for e in jobs.events(run)] == [1, 2]
    with pytest.raises(ValueError):
        jobs.transition(run, "published")
    assert jobs.get(run)["state"] == "preparing"
    jobs.transition(run, "cancelled")
    with pytest.raises(ValueError):
        jobs.transition(run, "baselining")
    assert jobs.claim() is not None


def test_recovery_keeps_queue_and_marks_interrupted(jobs):
    run = submit(jobs)
    pending = submit(jobs)
    jobs.claim()
    jobs.recover()
    assert jobs.get(run)["state"] == "interrupted"
    assert jobs.get(pending)["state"] == "queued"
    assert jobs.events(run, after=2)[0]["sequence"] == 3


def test_single_worker_lock(tmp_path):
    with worker_lock(tmp_path), pytest.raises(RuntimeError), worker_lock(tmp_path):
        pass
