import sqlite3
from contextlib import contextmanager
from pathlib import Path


class Store:
    """Short-lived connections. Transactions commit together or roll back together."""

    def __init__(self, path: Path):
        self.path = path

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.path, timeout=5)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def initialize(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute("PRAGMA journal_mode=WAL")
            version = db.execute("PRAGMA user_version").fetchone()[0]
            if version > 1:
                raise RuntimeError("Database schema is newer than this application")
            if version == 0:
                db.executescript("""
                    BEGIN IMMEDIATE;
                    CREATE TABLE runs (
                        id TEXT PRIMARY KEY,
                        task_json TEXT NOT NULL,
                        base_sha TEXT NOT NULL,
                        state TEXT NOT NULL,
                        budgets_json TEXT NOT NULL,
                        provider_json TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        terminal_reason TEXT
                    );
                    CREATE TABLE events (
                        run_id TEXT NOT NULL REFERENCES runs(id),
                        sequence INTEGER NOT NULL,
                        type TEXT NOT NULL,
                        payload_json TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        PRIMARY KEY(run_id, sequence)
                    );
                    PRAGMA user_version=1;
                    COMMIT;
                """)

    def health(self):
        with self.connect() as db:
            return db.execute("PRAGMA user_version").fetchone()[0]
