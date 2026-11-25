# M6: validate a candidate independently

The baseline is the original commit. A candidate is a separate copy with an exact,
bounded edit. Passing old tests is insufficient: the discount fixture's old tests
never check age 18. A protected evaluator checks that missing boundary and is never
included in retrieval or generation context. A generated test is auxiliary evidence.

`pipeline.py` drives explicit states and records every attempt. The offline provider
is a deterministic script, not an LLM and not a fallback disguised as live generation.
The second-attempt scenario deliberately proposes a wrong boundary first, observes
rejection, then supplies the correct scripted edit. Repeated proposals stop early.

All target tests execute inside the restricted Docker runner. Twelve acceptance
scenarios are evaluated separately; successful rejection is an expected outcome,
not a successful repair. A preserved refactor also has to reduce the target function's
line count. This metric is advisory and does not prove overall code quality.

Try explaining: why can the original tests pass while the evaluator fails? Where
would you add a new independent boundary case? What does a passing finite test set
leave unknown? Ayati's understanding and independent implementation are not assessed.
