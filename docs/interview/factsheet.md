# Project facts

CodePilot is a local Python maintenance prototype started on 25 November 2026.
It combines a React dashboard, FastAPI, a SQLite job queue, Tree-sitter, local
embeddings, Gemini generation and Docker validation.

Two live Gemini examples passed original and protected evaluator tests: a boundary
repair and helper extraction. Twelve separate scripted acceptance scenarios cover
both successful changes and expected rejections. The live repair also produced a
draft pull request on a dedicated fixture branch.

These results cover controlled examples, not general repair accuracy. There is no
model training, hosted service, arbitrary-repository support or automatic merging.
See the [capability ledger](../evidence/capabilities.md) and
[demo guide](../demo-guide.md) for evidence and presentation steps.
