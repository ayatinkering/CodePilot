# M2 structural-core verification — 2026-11-25

Installed Tree-sitter binding 0.27.0 and Python grammar 0.25.0; committed resolution
in uv.lock. `uv run --locked pytest -q`: 20 passed in 0.61s, inherited TestClient
warning only. Lint/format passed. Four new tests cover structures, malformed code,
metric ranges and stale snapshot rejection.

Real CLI debug run on CodePilot commit
`694f032a4a753399a3744e106b9ed9b0fb907170`:
- run `e7a5bb59307b448894b6f1ab31b31bd2`
- snapshot acquired by worker; baseline failed because runner image absent
- `codepilot index RUN_ID`: 15 Python files, 68 symbols
- index base SHA matches the recorded snapshot; run stays failed

No model was called, no target tests ran on host, and indexing did not convert
baseline failure to success. Calls resolve heuristically within a file or remain
unresolved; import aliases are recorded as source text, not linked across files.
Core extraction verified; fuller F03 alias/cross-file resolution remains partial.
Metrics are transparent suggestions, not semantic correctness or smell ground truth.
