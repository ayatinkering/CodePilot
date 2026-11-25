# M4 partial: Gemini proposes; application code checks

## Objectives and prerequisites
An API lets our backend ask an external model for output. A provider adapter is a
small module translating our task representation into that service's request.
A token is a unit the model processes; a context window limits how much fits into
one request. Inference uses trained model weights; CodePilot does not train them.
Retrying a request is not reinforcement learning because no weights are updated.
This lesson introduces part of Module 6; transformer/training theory remains later.

## Analogy and concrete example
Think of Gemini as a consultant receiving selected code and an issue. It can
suggest “change > to >=” but cannot authorize its own edit or publish a PR. The
analogy breaks because fluent model text can be statistically plausible yet wrong.
`task + evidence -> provider -> Plan JSON -> schema/reference/policy checks`

The smoke task contains `def discount(age): return age > 18` and asks to include
18. A valid proposal must cite `example:1` and stay within `src/example.py`. A
proposal for `.env` or invented evidence fails even if it is valid JSON.
This task is synthetic demonstration input, not a measured repair benchmark.

## Actual code walkthrough
`providers.Plan` defines decision, rationale, steps, evidence IDs, proposed files,
acceptance criteria and risks. Pydantic rejects missing or extra fields.
`GeminiProvider` requires a local key and explicit model, configures JSON schema,
disables automatic function calling, bounds timeout/output and closes its client.
No API key is placed in contents. `Settings` excludes its SecretStr field from
serialization and repr. Do not print the secret by explicitly extracting it.

`plan_task` checks context size and IDs before calling. After the response, it
validates IDs against supplied evidence and paths against an operator-supplied
allowlist. A proposing plan needs evidence, a file and acceptance criteria. One
invalid output can be retried once; repeated invalid output raises ProviderFailure.
Malformed response text is not echoed back. Provider failures never select offline
mode. Ordinary host code enforces policy; prompts are not a security boundary.

`Reply` records model, live/offline mode and usage. Missing usage gets conservative
accounting and an explicit flag; these estimates are not measured provider usage.
Current accounting is per planner invocation, not yet persisted across a complete
worker repair loop. Token counting by UTF-8 byte reservation is conservative but
not a true tokenizer. Output and context validation are approximately O(text size).

## Demonstrations and failure analysis
`codepilot plan-smoke` currently returns `gemini_key_missing` with exit code 2.
`CODEPILOT_PROVIDER=offline codepilot plan-smoke` returns a labeled abstention,
model `offline-abstention-fixture`, one call and zero provider tokens. These are
real control-path observations, not a successful live Gemini call.
Tests feed invalid JSON then a valid plan (two calls), reject invented evidence/
unauthorized paths, enforce budgets, verify secret exclusion and simulate a network
failure without exposing its message. The SDK contract test uses a fake client,
so its synthetic mode metadata must not be cited as live evidence.

## Alternatives and research connection
Provider interface versus SDK calls everywhere: a small abstraction supports
repeatable tests and future provider comparison. Structured output versus free
prose: easier parsing, but neither guarantees correct plans. RAG will supply code
context at inference; it is not fine-tuning. Retrieval itself remains unimplemented.
This component supports both repair and refactoring proposals, but preservation
and correctness need independent checks beyond the generator's assertions.

## Interview practice
Beginner: Why Gemini? Ayati selected it; no measured superiority is claimed.
Intermediate: Does JSON schema eliminate hallucination? No. It constrains form;
evidence checks reject invented IDs but cannot prove the proposed repair is right.
Advanced: What stops prompt injection? No model tools are exposed, proposals are
validated against independent allowed files/evidence, and publication will require
separate approval. Prompt instructions alone do not stop all injection effects.

## Exercise and teach-back (unassessed)
Change a scripted plan's evidence ID to one not in context and run its test. Why
should it fail even though the JSON is valid? Why is offline success not a live
provider result? Why does a retry not constitute model training?

<details><summary>Guidance</summary>
JSON validity checks structure, not provenance. Offline replies are programmed
fixtures. Inference retries do not update weights. Real quality requires live tasks
and independent tests, not merely a valid response schema.
</details>

Remaining: live request, available model/settings evidence, durable run budgets,
cancellation, retrieval integration, patch/test generation, full course concepts.
