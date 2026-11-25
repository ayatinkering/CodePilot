import json
import uuid
from datetime import UTC, datetime

from codepilot.config import Budgets
from codepilot.storage import Store

ACTIVE = {
    "preparing",
    "baselining",
    "indexing",
    "retrieving",
    "planning",
    "generating",
    "validating",
    "repairing",
    "publishing",
}
NEXT = {
    "queued": {"preparing", "cancelled"},
    "preparing": {"baselining"},
    "baselining": {"indexing"},
    "indexing": {"retrieving"},
    "retrieving": {"planning"},
    "planning": {"generating"},
    "generating": {"validating"},
    "validating": {"repairing", "ready_for_review"},
    "repairing": {"generating"},
    "ready_for_review": {"publishing", "cancelled"},
    "publishing": {"published", "publication_uncertain"},
    "publication_uncertain": {"publishing"},
}


def now():
    return datetime.now(UTC).isoformat()


class Jobs:
    def __init__(self, store: Store):
        self.store = store

    def _event(self, db, run_id, event_type, payload):
        sequence = db.execute(
            "SELECT COALESCE(MAX(sequence),0)+1 FROM events WHERE run_id=?", (run_id,)
        ).fetchone()[0]
        db.execute(
            "INSERT INTO events VALUES (?, ?, ?, ?, ?)",
            (run_id, sequence, event_type, json.dumps(payload), now()),
        )

    def submit(self, task: dict, base_sha: str, budgets: Budgets, provider: dict):
        run_id = uuid.uuid4().hex
        with self.store.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute(
                "INSERT INTO runs VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    run_id,
                    json.dumps(task),
                    base_sha,
                    "queued",
                    budgets.model_dump_json(),
                    json.dumps(provider),
                    now(),
                    None,
                ),
            )
            self._event(db, run_id, "state", {"state": "queued"})
        return run_id

    def get(self, run_id):
        with self.store.connect() as db:
            row = db.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
            if row is None:
                raise KeyError(run_id)
            return dict(row)

    def list(self):
        with self.store.connect() as db:
            return [
                dict(r) for r in db.execute("SELECT * FROM runs ORDER BY created_at DESC LIMIT 100")
            ]

    def record(self, run_id, event_type, payload):
        with self.store.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            self._event(db, run_id, event_type, payload)

    def events(self, run_id, after=0):
        with self.store.connect() as db:
            return [
                dict(r)
                for r in db.execute(
                    "SELECT * FROM events WHERE run_id=? AND sequence>? ORDER BY sequence LIMIT 1000",
                    (run_id, after),
                )
            ]

    def transition(self, run_id, state, reason=None):
        with self.store.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT state FROM runs WHERE id=?", (run_id,)).fetchone()
            if row is None:
                raise KeyError(run_id)
            old = row[0]
            permitted = set(NEXT.get(old, set()))
            if old in ACTIVE:
                permitted |= {"failed", "abstained", "cancelled", "interrupted"}
            if state not in permitted:
                raise ValueError(f"Invalid transition: {old} -> {state}")
            db.execute(
                "UPDATE runs SET state=?, terminal_reason=? WHERE id=?", (state, reason, run_id)
            )
            self._event(db, run_id, "state", {"state": state, "reason": reason})

    def claim(self):
        with self.store.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            placeholders = ",".join("?" for _ in ACTIVE)
            if db.execute(
                f"SELECT 1 FROM runs WHERE state IN ({placeholders}) LIMIT 1", tuple(ACTIVE)
            ).fetchone():
                return None
            row = db.execute(
                "SELECT id FROM runs WHERE state='queued' ORDER BY created_at LIMIT 1"
            ).fetchone()
            if row is None:
                return None
            db.execute("UPDATE runs SET state='preparing' WHERE id=?", (row[0],))
            self._event(db, row[0], "state", {"state": "preparing"})
            return row[0]

    def recover(self):
        """Only the worker holding the host process lock may invoke startup recovery."""
        with self.store.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            for row in db.execute("SELECT id,state FROM runs").fetchall():
                if row[1] in ACTIVE:
                    state = "publication_uncertain" if row[1] == "publishing" else "interrupted"
                    db.execute(
                        "UPDATE runs SET state=?,terminal_reason=? WHERE id=?",
                        (state, "worker_restart", row[0]),
                    )
                    self._event(db, row[0], "state", {"state": state, "reason": "worker_restart"})
