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

M4 adapter remote confirmed: `87f880a84f928fa9bcc3c61f94be2c4225494ac7`.
CI passed for that exact commit:
https://github.com/ayatinkering/CodePilot/actions/runs/45569020456
M2 core CI also passed:
https://github.com/ayatinkering/CodePilot/actions/runs/45568516227
Final backend run: 28 passed in 0.84s; lint/format passed; working tree clean after
checkpoint push. Live Gemini/model and Docker checks still blocked. M3 and M5–M10
remain planned, not complete. No remote deployment or product PR was created.

PR editing hit an installed-gh GraphQL Projects-classic deprecation; used the
GitHub REST PR update endpoint instead. This is a development tooling failure,
not a product test failure. No merge performed.

## Live infrastructure checkpoint, 2026-11-25
User resumed after configuring Gemini and Docker. Credential/model listing works;
Gemini schema compatibility fixed. gemini-3.8-flash generation returned 503.
Seven live Docker tests passed (17.11s), including isolation/timeout/cancel cleanup.
Fixed read-only source staging, Desktop host-path visibility and logging setup.
Pinned runner base digest/dependencies. Work paused at user request before commit;
resumed for basic MVP spanning M0–M10. Main project folder now holds the build
branch; temporary worktree disappeared, and no secrets were committed.

## M3 basic retrieval, 2026-11-25
Pinned BGE-small ONNX model downloaded; actual CPU semantic/cache/deletion checks
passed. Combined new retrieval and patch tests: 9 passed in 0.85s. Semantic retrieval
is implemented, not a token-hash stand-in. See M3 lesson and ADR 0005.
Previous infrastructure commit e5c5199 pushed successfully.

## M5 exact edits, 2026-11-25
Eight meaningful patch policy tests passed. Source syntax is parsed, never executed
on host. Candidate copies preserve protected tests and baseline. Lesson M5 and
ADR 0006 document the actual trade-off; no full repair claim yet.

## Offline MVP completion — 2026-11-25

User explicitly excluded live Gemini and requested the basic remaining features.
No live generation calls were made for this completion. The earlier model outage is
not hidden by a fallback: the UI/API only accept labeled offline scripted runs.

- `e5c5199`: real Docker boundary checks and provider JSON-schema compatibility.
- `6512b08`: pinned real local embeddings and hybrid retrieval.
- `587dc1f`: bounded exact edit policy and isolated candidates.
- `cfa9079`: bounded offline workflow, independent evaluator and fixture refactoring.
- `fa0232d`: first-parent commit/file impact analysis.
- `5c4bb22`: local review UI/API and approved draft publication.

Evidence: 51 tests passed with Docker enabled; seven real Docker tests included.
Ruff lint/format, locked Python sync and frontend production build passed. Twelve
scripted acceptance scenarios reached their expected states, with raw JSON/CSV
committed under `evaluation/results`. They are not a live-model success benchmark.

Controlled GitHub issue #2 was imported through the API. Run
`f1ef680601494d13b8c52dcf91bd331d` produced the reviewed boundary edit and real draft
PR #3 on `codex/demo-fixture`. Repeating approval returned the same PR. No merge.
The final startup script served the dashboard and API; SSE Last-Event-ID=2 resumed
at event 3. Visual walkthrough remains blocked by the desktop browser attachment,
which reported an app-update/network-policy requirement. No screenshot or visual
verification is claimed. See `docs/demo-guide.md` for the concise presentation.

## Live Gemini completion — 2026-11-25

User re-authorized live generation. The local credential was configured by the user,
never printed or committed. Model discovery worked. Gemini 3.1 Flash Lite and 3.8
Flash returned 503; Gemini 3.5 Flash returned a valid typed plan and was explicitly
selected. No silent provider/model fallback exists in application runs.

The API/dashboard now support live Gemini and distinctly labeled offline mode.
Request accounting includes failures and unknown-usage reservations; the exact call
limit no longer prevents validating the last allowed response. Prior candidate edits
and coarse outcomes support repairs without exposing protected evaluator content.
Publication descriptions now reflect actual provider/model provenance.

Real run `b6432691a6a843d29c9e0e17f0797a0f`: Gemini-generated boundary repair passed
original, independent and auxiliary Docker checks; 2 calls, 3,150 reported tokens.
Reviewed change published as draft PR #4 on the isolated fixture branch.
Real run `c19c00b2801749d882a65da202514523`: Gemini-generated helper extraction passed
behavior checks; target function 7→6 lines; 2 calls, 4,086 reported tokens.
Raw evidence is in `docs/evidence/live-generation.json`; setup probes are separate.

Final validation: 56 tests passed including real Docker isolation tests, Ruff passed,
and the React production build passed. Browser visual verification remains pending
because the desktop browser attachment was unavailable. This completes the basic
controlled-fixture MVP with live generation, not the original PRD's advanced/general
research scope. No merges, hosting, or model training performed.
