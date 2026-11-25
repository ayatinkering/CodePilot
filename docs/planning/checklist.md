# Current MVP checklist

Scope update: the user subsequently requested live Gemini; it is now enabled and verified.
This is a controlled offline demonstration, not full fulfillment of the original PRD.

- [x] M0: configuration, schema, health and locked dependencies.
- [x] M1 basic: immutable snapshots, persistent worker/events and real Docker runner.
- [x] M2 basic: Tree-sitter symbols and heuristic structure.
- [x] M3 basic: real local embeddings and hybrid retrieval.
- [x] M4 live: Gemini-generated repair and refactor passed independent Docker validation; scripted mode remains separate.
- [x] M5 basic: bounded exact patch application with original tests protected.
- [x] M6 basic: independent checks, bounded repair and negative cases.
- [x] M7 implementation: review dashboard and API; production build and API tests.
- [ ] M7 visual browser walkthrough: blocked by desktop browser attachment.
- [x] M8 basic: real issue import and approved draft PR on isolated demo branch.
- [x] M9 basic: commit file impact and one behavior-preserving helper extraction.
- [x] M10 basic: 12 offline acceptance cases, raw results, setup and interview guide.

See `docs/evidence/capabilities.md` for evidence and limitations, and `docs/build-log.md`
for commits. Advanced/generalized features from the original PRD remain out of scope.
