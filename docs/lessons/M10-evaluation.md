# M10: measure the claim you actually made

The evaluation asks whether the workflow accepts or rejects each controlled scenario
as designed. Twelve cases share two source fixtures; this is not twelve independent
real-world repair tasks. A/B/C exercise different retrieval paths but use the same
scripted generation. Consequently their outcomes do not prove a retrieval quality gain.

Raw JSON records candidates, separate test reports, model identity, timings and reasons;
CSV summarizes outcomes. Correct rejection of a bad patch is a passing acceptance case,
not a successful bug repair. No live generation calls or generation tokens are used.
The local embedding model is real and computes vectors on the CPU.

Run `codepilot evaluate` with the worker stopped. The command obtains the worker lock,
executes targets only in Docker, and exits unsuccessfully if an expected state differs.
For future research, use more diverse held-out tasks, fixed budgets, repeated runs,
live-model provenance and an independent evaluator; report failures and denominators.
Do not infer general performance or interview readiness from this small acceptance set.
