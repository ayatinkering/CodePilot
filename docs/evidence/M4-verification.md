# M4 adapter-only verification — 2026-11-25

Official SDK google-genai 2.34.0 installed and locked. Model is intentionally unset
until account availability can be verified. Gemini key absent; no live request made.

`uv run --locked pytest -q`: 28 passed in 0.86s; one inherited TestClient warning.
Provider tests: invalid JSON bounded recovery; unknown evidence and unauthorized
path rejection; explicit offline abstention; missing key/model rejection; secrets
absent from settings repr/dump; budget rejection; SDK request schema/options and
safe network-error handling using a fake SDK client.

Actual `codepilot plan-smoke`: exit 2, `gemini_key_missing`.
Actual `CODEPILOT_PROVIDER=offline codepilot plan-smoke`: decision abstain, mode
`offline`, model `offline-abstention-fixture`, calls 1, tokens 0, usage_known true.
This is not a successful generated patch, remote schema acceptance or model-quality
result. Live M4 acceptance remains blocked. Adapter is callable via debug CLI but
not yet wired into the worker after baseline. No repair or publication attempted.
