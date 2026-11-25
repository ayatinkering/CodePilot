# Capability ledger

Date: 2026-11-25. No CV capability is inferred from a requirement or a file name.

| Capability | Status | Code | Evidence | Limitation |
|---|---|---|---|---|
| Config/schema/health | Verified locally | backend/codepilot/{config,storage,api,cli}.py | tests/unit/test_foundation.py; M0-verification.md | No jobs yet |
| GitHub issue ingestion | Planned | — | — | Development pushes are not product PR automation |
| Structural analysis | Core locally verified; partial | backend/codepilot/indexing.py | M2-verification.md | No complete call graph; alias/cross-file linking not implemented |
| Semantic retrieval | Planned | — | No local embedding package/cache found | No fake vectors |
| Gemini planning/generation | Planned; live blocked | — | No GEMINI_API_KEY/GOOGLE_API_KEY found | Model not selected/verified |
| Generated tests/repair/regression | Planned | — | — | No success rates |
| Restricted target execution | Implemented; live blocked | backend/codepilot/runner.py; runner/ | M1-verification.md | No live boundary claim; no host fallback |
| React execution interface | Planned | — | — | API docs are not the React UI |
| Product draft PR publication | Planned | — | — | Must bind user approval to patch digest |
| Refactoring and evaluation | Planned | — | — | No semantic preservation claim |

Snapshot and worker lifecycle: locally verified in tests/unit/test_acquisition.py, test_jobs.py and test_worker.py. Remote acquisition and retry remain planned.
