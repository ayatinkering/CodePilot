# M0 verification — 2026-11-25

Observed locally on Python 3.12.14 (system Python also reports 3.12.3).

- `uv sync --cache-dir /tmp/codepilot-uv-cache`: 27 resolved packages; 26 installed.
- `uv run --locked pytest -q`: 7 passed in 0.28s outside sandbox.
- `uv run --locked ruff check .`: all checks passed.
- `uv run --locked ruff format --check .`: passed.
- `uv run --locked codepilot health`: `{"status": "ok", "schema_version": 1}`.
- Fresh virtual environment `/tmp/codepilot-m0-clean`, `uv sync --locked --offline`
  with previously downloaded cache: installed successfully; health with a fresh
  data directory returned schema 1. This is not a fresh-machine network test.
- Tests verify restart, foreign keys, WAL, future-schema rejection, unexpected
  Host rejection, budget limits and secret/runtime ignore rules.
- `git diff --check`: passed before staging.

Failures/limits: initial lint found import ordering and missing explicit subprocess
check flags; fixed. Sandboxed TestClient stalled, while the same tests outside the
sandbox passed. Starlette emits a deprecation warning for its httpx TestClient;
no behavior failure observed. No target code ran on the host. GitHub authentication
works outside sandbox. Docker Desktop socket is absent even outside sandbox.
Gemini credential and local embedding model are absent. No live capability,
worker, UI, target-container restriction, repair outcome or CI result is claimed.
