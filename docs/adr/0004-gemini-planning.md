# ADR 0004: Gemini provider with typed proposals

2026-11-25. User-selected Gemini; official google-genai SDK locked at 2.34.0.
Reference checked: https://googleapis.github.io/python-genai/ (generate_content,
Pydantic schemas, client closing, HttpOptions). SDK is Apache-2.0 licensed.

No automatic model selection: require CODEPILOT_MODEL and GEMINI_API_KEY locally.
The model must actually be available to the user's account; no model ID or success
is claimed before live access. SecretStr prevents settings repr/serialization
leaks. Key goes only to SDK client, never to target runner configuration.

Use structured JSON Plan with schema plus independent reference/path validation.
Schema compliance is not semantic correctness. Give the model no callable tools.
Repository/issue data is JSON within a user input and cannot grant permission.
System guidance is defense in depth; application policy validates output regardless.
Offline mode is a separate explicit deterministic abstention fixture, not fallback.

Bound planning to two calls, each 60-second SDK timeout with one transport attempt,
2048 output tokens and explicit context byte ceiling. Record actual total usage if
supplied, otherwise conservatively reserve context bytes plus output allowance and
mark usage unknown. This is local planner accounting, not yet durable whole-run
budget enforcement. Refuse excessive context rather than silently dropping it.
Worker cancellation of an active synchronous provider call remains unimplemented.

Rejected alternatives: unstructured prose (difficult validation), arbitrary model
shell tools (unnecessary permissions), silently switching providers on outages
(invalid experimental provenance). Error categories suppress provider exception
text; redaction covers recognizable key patterns but cannot guarantee detection
of every secret embedded in arbitrary source. Explicit trusted target scope remains.

Live Gemini smoke blocked on absent key/model. SDK request contract and failure
behavior tested locally with a fake client; this does not establish remote API
acceptance or planning quality. Adapter not yet integrated into the worker pipeline.
