# ADR 0001: Local modular backend and explicit evidence

Date: 2026-11-25. Accepted for the prototype; subsequent choices need their own ADR.

Use Python 3.12, FastAPI and Pydantic for validated HTTP boundaries; SQLite WAL
and short transactions for local persistence. A separate single worker will own
long-running tasks. API handlers will not run repository tests or model loops.
PostgreSQL and a distributed queue would improve multi-user concurrency but add
services before a measured need. SQLite is not a claim of enterprise scalability.

Use an isolated development worktree on a feature branch, leaving `main`
with the initial README. Product candidate checkouts will be separate again.
Keep run limits immutable and persist their JSON per run. Schema version 1 defines
run/event ownership and unique per-run event sequence numbers; later migrations
must preserve data. M0 does not yet implement claims or state transitions.

Gemini was explicitly selected by the user. Provider-specific requests belong in
an adapter; do not silently substitute OpenAI or fake outputs. Model identity will
be selected/verified against actual access, not guessed from a model name.
No credentials are required for health/configuration tests.

Use uv's complete transitive lock for repeatable installs, rather than relying on
unbounded pip installation. Runtime package declarations permit compatible updates;
`uv sync --locked` installs the committed exact resolution. Dependency licenses
must be reviewed when adding models/runner assets. No project license is chosen.

Official references checked during implementation:
- https://docs.astral.sh/uv/concepts/projects/sync/
- https://fastapi.tiangolo.com/advanced/events/
- https://github.com/googleapis/python-genai

Limit: read-only health/capabilities routes only. Mutation authentication, safe
acquisition, runner restrictions and provider calls are not implemented by this ADR.
