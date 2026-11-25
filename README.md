# CodePilot

An AI-assisted Python maintenance research prototype, started 25 November 2026.
**In development: M0 foundation only. No issue-to-patch or live-model success claimed.**
Gemini is the selected generation provider. There is no model training or fine-tuning.

## Run the foundation

Prerequisites: Git, Python 3.12, [uv](https://docs.astral.sh/uv/).

```sh
git clone --branch codex/codepilot-build https://github.com/ayatinkering/CodePilot.git
cd CodePilot
uv sync --locked
uv run --locked codepilot health
uv run --locked codepilot serve
```

Open http://127.0.0.1:8000/docs for the API; GET `/api/health` checks database access.
There is no React UI yet. GitHub hosts the source; it is not a deployed application.

```sh
uv run --locked pytest -q
uv run --locked ruff check .
uv run --locked ruff format --check .
```

Configuration: copy `.env.example` to ignored `.env` if needed. `CODEPILOT_DATA_DIR`
chooses local storage (default `.codepilot`); `CODEPILOT_PROVIDER` is `gemini` or
`offline`; `CODEPILOT_MODEL` will identify an explicitly chosen available model.
`GEMINI_API_KEY` is reserved for backend-only live calls. Obtain keys through
[Google AI Studio](https://aistudio.google.com/apikey); enter them locally, never in
chat, tracked files, frontend code, logs, or target containers. No key is needed
for foundation tests. No live adapter or automatic model selection exists yet.

Docker Engine/Desktop must be running before target validation can be implemented
and verified. No host execution fallback is permitted. Initial targets will be
explicitly trusted, allowlisted Python repositories with vetted pytest dependencies.
The local backend is not a public arbitrary-code execution service. Bind to loopback.
A future mutation API must require local authentication and origin checks.

Troubleshooting: `codepilot health` requires a writable data directory. A newer
schema is rejected; do not delete real data to downgrade. `uv sync --locked` fails
on stale dependency declarations; update the lock deliberately. A Docker socket
error means the daemon/context needs attention, not that tests passed.

See [checklist](docs/planning/checklist.md), [capability evidence](docs/evidence/capabilities.md),
[lessons](docs/lessons/M0-foundation.md), and [build log](docs/build-log.md).
Dependencies are locked in `uv.lock`; no project license has been selected yet.
GitHub App webhooks, live PR automation, semantic retrieval, and evaluation are planned.
