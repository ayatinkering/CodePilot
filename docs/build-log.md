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
