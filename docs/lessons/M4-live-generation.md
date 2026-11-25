# Live Gemini generation

The offline generator returns a prewritten edit. The Gemini adapter sends the task,
retrieved source, and allowed file list to a hosted model. The response supplies a
new typed plan. A second request receives that plan plus exact source/preimage hashes
and generates an edit and optional auxiliary test. Neither request receives the
protected evaluator source. The model has no tools and cannot execute or publish.

The distinction is proposal versus acceptance: a real model can be wrong. The same
patch policy, Docker runner, independent evaluator and human review apply to live and
offline runs. Invalid output can consume a bounded candidate attempt; model outages
stop visibly. There is no scripted fallback. Subsequent candidates receive prior
edits and coarse check outcomes, not hidden evaluator source or assertions.

Request accounting happens before dispatch. Failed calls count too; when actual
usage is unknown, a conservative reservation is recorded rather than claiming zero.
The per-run selected model is persisted so a later settings change cannot silently
change a retry. Cancellation is checked before and after a bounded synchronous call;
it may wait up to 60 seconds for the active request to finish.

A configured key is not proof that generation works. Model discovery can succeed
while a listed model returns 503. During this implementation, Flash Lite and 3.8 Flash
returned service-unavailable errors; 3.5 Flash returned a valid structured plan.
See `docs/evidence/live-generation.json` for final end-to-end evidence.

The SDK's JSON-schema option constrains output shape, not correctness. See the
[official Google Gen AI SDK documentation](https://googleapis.github.io/python-genai/)
and [Google's structured-output explanation](https://blog.google/innovation-and-ai/technology/developers-tools/gemini-api-structured-outputs/).

Teach-back: trace one live run and explain why two successful API calls are not yet
a successful repair. Identify where a test-file edit, stale SHA, or failed evaluator
would prevent publication. The model is used for inference; no weights are trained.
