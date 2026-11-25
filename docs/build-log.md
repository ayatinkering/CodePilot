# Build log

## 2026-11-25 — initial state
Repository main: `449132d232770dfa071cdd3527a6f96bf0c2e4ad`, README only.
Ayati authorized implementation and milestone pushes; chose Gemini API. Codex
created isolated worktree `/tmp/codepilot-build`, branch `codex/codepilot-build`.
Copied only the three explicitly supplied handoff documents into docs/planning.

## M0 — foundation
Implemented bounded settings, versioned SQLite schema, FastAPI health/capabilities,
CLI, lockfile, CI configuration, lessons and capability/learning ledgers.
Checks: seven tests pass; lint/format pass; fresh cached install and health pass.
Evidence: docs/evidence/M0-verification.md. Lesson: docs/lessons/M0-foundation.md.
Commit reference: the commit introducing this section (`feat(core): bootstrap local backend foundation`).
Push status at commit creation: pending; record remote SHA in the next log update.
Failures: sandbox network/async test restriction, corrected lint, Docker unavailable.
Live Gemini remains blocked on local credential setup. No successes fabricated.

M0 remote confirmed: `7cb9d0e8d87630e633c9d0bb857181e4b3e4a1f1`.
Draft implementation PR: https://github.com/ayatinkering/CodePilot/pull/1
GitHub CI passed: https://github.com/ayatinkering/CodePilot/actions/runs/45567422409

## M1 partial — acquisition and worker
16 local tests passed; lint/format passed. Real snapshot and missing-image worker
flow verified. Container boundary checks blocked because Docker is not running.
See evidence/M1-verification.md and lessons/M1-snapshots-and-jobs.md.
Commit reference: commit introducing this section; push pending at creation.
Do not mark M1 complete until live runner, timeout and cancellation checks pass.

M1 partial remote confirmed: `694f032a4a753399a3744e106b9ed9b0fb907170`.

## M2 structural core
Real Tree-sitter symbols, raw imports, heuristic/unresolved calls and advisory
metrics. 20 tests passed; actual CLI indexed 15 Python files / 68 symbols from
M1 commit. See evidence/M2-verification.md and lessons/M2-structural-index.md.
Cross-file/alias linking remains partial. Commit reference: introducing commit;
push pending at creation. No live generation or end-to-end repair claimed.

M2 core remote confirmed: `1bbeaf2ec2e36df80f72cee7a8eca9b72760da4c`.

## M4 adapter-only checkpoint (M3 still planned)
Selected Gemini implemented behind a typed planner interface. 28 tests pass.
Offline abstention and real missing-key failure observed; no live generation.
See evidence/M4-verification.md and lessons/M4-gemini-planning.md.
Dependency-independent work proceeded while Docker/key remained unavailable.
Commit reference: introducing commit; push pending at creation.
