# Capability ledger — offline MVP, 25 November 2026

The latest user scope excludes live Gemini. Earlier evidence files describe historical
checkpoints and may list blockers that are now resolved. This ledger is current.

| Area | Implemented and evidenced | Limits |
|---|---|---|
| M0 | Locked Python/Node dependencies, configuration, SQLite schema, health | Local Linux only |
| M1 | Immutable Git snapshots, separate worker, state/events, recovery, restricted Docker | Trusted registered fixtures; no remote arbitrary execution |
| M2 | Tree-sitter symbols/ranges, imports, heuristic references, metrics | Cross-file graph and semantic resolution incomplete |
| M3 | Pinned BGE ONNX embeddings, lexical/semantic rank fusion, cache identity and structural expansion | Small local index; no trained model |
| M4 | Typed scripted plan and candidate provenance | Live Gemini explicitly excluded; adapter is experimental |
| M5 | Exact preimage edits, path/file/line limits, preserved tests and isolated copies | Existing `src/*.py` files only |
| M6 | Original/evaluator/generated checks, bounded repair, repeated-candidate stop | Finite curated checks, not correctness proof |
| M7 | React review UI, FastAPI sessions/origin checks, SSE, history, cancel/retry/artifacts | Build/API tested; browser attachment blocked visual verification |
| M8 | Real issue import, digest/base approval, candidate reconstruction, draft PR, reconciliation | Host gh auth; one opted-in fixture branch; no GitHub App/webhooks |
| M9 | First-parent file impact, helper extraction, behavior checks and target metric | One controlled refactor; conservative impact, no general refactoring engine |
| M10 | 12 offline acceptance scenarios, raw JSON/CSV, setup and interview guide | Two synthetic source fixtures; no live-model benchmark |

Verification: 51 tests passed including seven real Docker tests; frontend production
build, Ruff lint and format checks passed. Docker tests cover network/environment,
read-only/non-root restrictions, failure classification, timeout and cancellation.
`evaluation/results` records 12/12 expected outcomes (including abstentions/failures).
`github-demo.json` records the real draft PR and idempotent repeat approval.
No model tokens were used for these offline runs. Actual timings are in the reports.

Browser verification blocker: in-app browser attachment timed out; Chrome attachment
reported "Browser attachment requires a network policy. Update the Codex desktop app
to the latest version and retry." No visual verification is claimed.

No automatic merge, public deployment, model training, historical ownership claim,
or retroactive validation of the CV. Source was built with AI assistance; Ayati's
independent understanding must be established through the course exercises.
