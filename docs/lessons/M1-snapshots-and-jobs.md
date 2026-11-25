# M1 (partial): Fixed snapshots, job ownership and baseline checks

## Objectives, prerequisites and vocabulary
Build on M0's repository, API and schema. A snapshot is source at one fixed commit.
A job is a persisted request for work. A transaction groups changes so readers see
all or none. A baseline is the test result before changing source. A container is
a restricted process environment sharing the host kernel, not a separate VM.

## Why this component exists
If your file changes while the agent reads it, its plan may describe one version
and its tests another. `HEAD -> exact SHA -> copied Git blobs -> baseline` fixes the
starting version. Reading source is different from executing it. Tests execute
arbitrary code, so only the future verified restricted container may run targets.
The worker is like a queue attendant; the analogy fails if two attendants both
claim the same ticket. Database transactions and a process lock enforce ownership.

## Concrete implementation walkthrough
`acquisition.acquire` validates the registered local path, resolves HEAD once,
reads regular blobs from that SHA and writes a new managed directory. The original
worktree is never checked out/reset. Manifest records file hashes and skipped
reasons; a symlink to `/etc/passwd` is skipped, not followed. File count/byte limits
bound memory. Complexity includes one or more Git subprocesses per file, O(N)
process launches plus O(bytes) copying/hashing. This is simple but not optimized.

`Jobs.submit` saves task, base SHA, budgets and provider metadata. `claim` begins a
write transaction, checks for active work and takes the oldest queued job. The
state update and sequence-numbered event commit together. A state transition is a
permitted edge: preparing -> baselining is legal; preparing -> published is not.
Invalid transitions roll back. `events(after=...)` supplies ordered replay.

`worker_lock` uses a host file lock, released if the process exits. `recover` marks
active jobs interrupted; publishing gets publication_uncertain because a remote
write might already have happened. We do not claim arbitrary resume. `execute_one`
acquires a snapshot and records baseline results; the rest of the pipeline is
explicitly unimplemented and abstains after a passing baseline.

`runner.run_tests` requires an operator-built image ID; no image or daemon produces
an environment error. No subprocess can fall back to host pytest for target code.
The proposed Docker flags constrain network, capabilities, resources and writable
paths. They are implemented but **not live verified**. Container escapes and
malicious tests are not ruled out. Docker's daemon is a trusted privileged boundary.

## Demonstrations and evidence
`tests/unit/test_acquisition.py` builds controlled Git fixtures: committed code is
copied even if the worktree has an uncommitted edit; original status/content remain
unchanged; symlink/env files are skipped. An unregistered repository and traversal
are rejected. `test_jobs.py` races two claims: exactly one wins. Cancellation
prevents a later baseline transition. Recovery preserves queued work.
`test_worker.py` exercises actual snapshot/SQLite flow with no runner image:
queued -> preparing -> baselining -> failed(environment_error). No target test runs.
`test_runner.py` checks zero-test and collection-error classification. These tests
do not establish real timeout, network blocking, secret isolation or Docker cleanup.
See ../evidence/M1-verification.md for actual results and blocked checks.

## Trade-offs and failure modes
Separate worker over FastAPI background tasks: process lifecycle is explicit and
requests stay short. Fixed snapshots over editing the source worktree: extra disk
space buys reproducibility. SQLite over distributed queue: one local worker only.
Missing dependencies are environment problems; existing assertion failures are
baseline defects. Neither is successful validation. Test reports are auxiliary and
cannot serve as a hostile-code security proof.

## Interview practice
Beginner: Why use a base SHA? It fixes the version being analyzed, independent of
later branch movement and uncommitted user edits.
Intermediate: How do you avoid duplicate jobs? A SQLite immediate transaction
claims only while no job is active; a process lock restricts worker ownership.
Advanced: What if publication crashes? Startup marks publication_uncertain, because
we must reconcile remote state before retrying. Reconciliation is planned, not
implemented. Reissuing a write blindly could create duplicates.

## Exercise and teach-back (unassessed)
Change a fixture's worktree after committing; run its acquisition test and inspect
which bytes reach the snapshot. Why does a passing unit test not prove container
isolation? What is the difference between baseline_failed and environment_error?
Why should publishing recovery differ from indexing recovery?

<details><summary>Exercise guidance</summary>
The committed bytes reach the snapshot; the worktree edit stays untouched. Container
boundaries need real execution checks. Baseline failure describes target tests;
environment_error describes an unusable validation setup. Remote publication may
already have taken effect even if the worker did not receive the response.
</details>

Connection: both refactoring and repair require a reproducible pre-change baseline.
This supports the PRD lifecycle but does not yet fulfill a CV claim of automated
repair. Learner understanding remains unassessed; implementation is AI-assisted.

## Observed live results, 2026-11-25
Seven opt-in real Docker checks passed in 17.11 seconds. They cover passing tests,
assertion failure, missing dependency, no tests, non-root/no capabilities/seccomp,
network denial, absence of host secrets, source/root write denial, timeout,
cancellation and container/volume cleanup. Run with CODEPILOT_TEST_RUNNER_IMAGE
set to the built image ID. Source transfer and logging failed initially and were
fixed (ADR 0002). A sandbox design written on paper was not enough.
