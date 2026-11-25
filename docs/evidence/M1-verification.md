# M1 partial verification — 2026-11-25

`uv run --locked pytest -q`: 16 passed in 0.96s (one inherited TestClient warning).
Ruff check/format and `git diff --check` passed.
Verified: exact committed snapshot with original worktree unchanged, sensitive/
symlink skips, traversal and non-allowlisted path rejection, byte exclusion,
concurrent claim exclusion, atomic ordered events, invalid transition rejection,
cancellation state, interrupted recovery and exclusive worker lock.

Actual worker test (real Git + SQLite, no mocked runner): queued -> preparing ->
baselining -> failed; report reason `runner_image_digest_required`. Target code
was never executed on the host. Report classifier tests include zero tests,
pre-existing failure, missing collection environment and all-skipped cases.

Blocked: actual Docker build/runner, timeout, process cleanup, network denial,
secret absence, filesystem boundaries, live cancellation. Docker Desktop daemon
socket is absent. Current image build does not fully lock transitive dependencies.
No retry API or remote acquisition. M1 is not complete; unit tests do not substitute
for the listed real execution checks. Partial checkpoint may be committed safely.
