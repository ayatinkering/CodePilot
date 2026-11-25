# CodePilot

An AI-assisted Python maintenance research prototype, started 25 November 2026.
**In development: foundation, partial worker and structural indexing. No issue-to-patch or live-model success claimed.**
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
for foundation tests. Gemini planning adapter exists; live access remains unverified. There is no automatic model selection.

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

## Partial M1: queue and worker

The worker stops after baseline; a passing baseline currently abstains with
`pipeline_not_implemented_after_baseline`. Container execution is unverified.

```sh
# Operator-controlled allowlist, not inferred from an issue or repository README.
export CODEPILOT_ALLOWED_REPOS=/absolute/path/to/trusted/python/repository
# Separate operator preparation (requires running Docker):
docker build -t codepilot-runner:dev runner
export CODEPILOT_RUNNER_IMAGE=$(docker image inspect codepilot-runner:dev --format '{{.Id}}')
uv run --locked codepilot submit /absolute/path/to/trusted/python/repository 'Describe the issue'
uv run --locked codepilot worker
# In another terminal, using the run ID printed by submit:
uv run --locked codepilot status RUN_ID
uv run --locked codepilot cancel RUN_ID
```

Linux worker only (`flock`). Stop with Ctrl-C; next startup marks active work
interrupted. Retry and remote acquisition are not implemented. Snapshots/reports
under `.codepilot/runs` may contain repository source: keep them local. Image build
requires network; execution never installs target dependencies. Docker access is
privileged; never expose this worker publicly or mount the socket into target code.

## Structural inspection

After a worker has acquired a run snapshot (even if baseline fails due to unavailable
Docker), `uv run --locked codepilot index RUN_ID` prints and saves a real Tree-sitter
index in that run's directory. This debug inspection does not bypass the baseline
gate or mark the run validated. Symbols, ranges, parse errors, advisory metrics and
heuristic/unresolved call references are inspectable; cross-file import resolution
and semantic retrieval are not implemented yet.

## Gemini planning smoke check (partial M4)

Configure `GEMINI_API_KEY` and an available exact `CODEPILOT_MODEL` locally in
ignored `.env`. Do not paste keys into chat. Then:

```sh
uv run --locked codepilot plan-smoke
# Explicit test fixture; this is not a live model:
CODEPILOT_PROVIDER=offline uv run --locked codepilot plan-smoke
```

Live smoke sends only a small synthetic boundary-condition task. It may incur
provider usage. A missing key/model fails visibly; it never silently selects the
fake provider. The adapter is not yet wired into the worker repair pipeline.
