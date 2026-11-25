import sqlite3
import subprocess

import pytest
from codepilot.api import create_app
from codepilot.config import Budgets, Settings
from codepilot.storage import Store
from fastapi.testclient import TestClient
from pydantic import ValidationError


def test_health_survives_restart(tmp_path):
    settings = Settings(data_dir=tmp_path)
    for _ in range(2):
        with TestClient(create_app(settings)) as client:
            assert client.get("/api/health").json() == {
                "status": "ok",
                "schema_version": 1,
                "release": "foundation",
            }
            client.post("/api/session", headers={"origin": "http://testserver"})
            assert client.get("/api/capabilities").json()["live_generation_verified"] is False
            assert client.get("/api/health", headers={"host": "evil.example"}).status_code == 400


@pytest.mark.parametrize("field,value", [("candidates", 4), ("tokens", 0), ("test_seconds", 121)])
def test_budget_hard_bounds(field, value):
    with pytest.raises(ValidationError):
        Budgets(**{field: value})


def test_unknown_budget_rejected():
    with pytest.raises(ValidationError):
        Budgets(infinite_retries=True)


def test_database_constraints_and_version(tmp_path):
    store = Store(tmp_path / "db.sqlite3")
    store.initialize()
    with store.connect() as db:
        assert db.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("INSERT INTO events VALUES ('missing', 1, 'test', '{}', 'now')")
        db.execute("PRAGMA user_version=99")
    with pytest.raises(RuntimeError, match="newer"):
        store.initialize()


def test_sensitive_runtime_files_ignored():
    for path in [".env", ".env.local", ".codepilot/private-source.py", "key.pem"]:
        assert subprocess.run(["git", "check-ignore", "-q", path], check=False).returncode == 0
    assert (
        subprocess.run(["git", "check-ignore", "-q", ".env.example"], check=False).returncode == 1
    )
