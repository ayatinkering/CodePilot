import json
import subprocess

from codepilot.config import Budgets, Settings
from codepilot.jobs import Jobs
from codepilot.storage import Store
from codepilot.worker import execute_one


def test_worker_persists_real_snapshot_and_missing_runner(tmp_path):
    source = tmp_path / "repo"
    source.mkdir()
    for args in [
        ["init"],
        ["config", "user.name", "Fixture"],
        ["config", "user.email", "fixture@example.invalid"],
    ]:
        subprocess.run(["git", "-C", str(source), *args], check=True, capture_output=True)
    (source / "safe.py").write_text("x = 1\n")
    subprocess.run(["git", "-C", str(source), "add", "safe.py"], check=True)
    subprocess.run(
        ["git", "-C", str(source), "commit", "-m", "fixture"], check=True, capture_output=True
    )
    sha = subprocess.check_output(
        ["git", "-C", str(source), "rev-parse", "HEAD"], text=True
    ).strip()
    settings = Settings(data_dir=tmp_path / "data")
    store = Store(settings.data_dir / "db")
    store.initialize()
    jobs = Jobs(store)
    run = jobs.submit({"repository": str(source)}, sha, Budgets(), {"provider": "offline"})
    assert execute_one(jobs, settings, [source], "")
    assert jobs.get(run)["state"] == "failed"
    assert jobs.get(run)["terminal_reason"] == "environment_error"
    report = json.loads((settings.data_dir / "runs" / run / "baseline-report.json").read_text())
    assert report["reason"] == "runner_image_digest_required"
    assert [json.loads(e["payload_json"])["state"] for e in jobs.events(run)] == [
        "queued",
        "preparing",
        "baselining",
        "failed",
    ]
