# Implementation checklist

Provider decision: Ayati selected Gemini API on 2026-11-25. The supplied planning
pack is retained verbatim for context; current implementation and evidence take
precedence over any aspirational capability description.

| Milestone | Feature | Verification gate | Status |
|---|---|---|---|
| M0 | Bootstrap, bounded configuration, schema, health | Clean install, health, ignored secrets | Verified locally (7 tests); push pending |
| M1 | Safe checkout, worker/events, restricted runner | Original unchanged, failure/timeout/cancel | Planned |
| M2 | Tree-sitter symbols/approximate edges | Structural and malformed fixtures | Planned |
| M3 | Real semantic embeddings and hybrid search | Semantic query, deletion/revision invalidation | Planned |
| M4 | Gemini typed planning | Real call, malformed output, outage | Blocked live: credential absent |
| M5 | Structured edits and candidate isolation | Valid edit, traversal/ambiguity/preimage rejection | Planned |
| M6 | Independent validation and bounded repair | False success rejected, no-progress stop | Planned |
| M7 | React UI, events and artifacts | Browser end-to-end, replay/cancel/failure | Planned |
| M8 | Issues and approved draft PRs | Real authorized PR, stale base, idempotency | Planned |
| M9 | Commit analysis and bounded refactoring | Preservation, regression rejection, abstention | Planned |
| M10 | Evaluation, setup, interview pack | Raw results, fresh clone, honest limitations | Planned |

Each milestone needs source, tests, lesson, ADR/evidence, a reviewed staged diff,
a commit, push and matching remote SHA. Never merge the implementation PR automatically.
