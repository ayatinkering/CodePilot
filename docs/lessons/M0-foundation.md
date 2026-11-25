# M0: What we are building and why the foundation matters

## Objectives and prerequisites
Understand a repository, issue, patch, test, regression, PR, API, schema and budget.
No previous backend knowledge assumed. This lesson introduces modules 0–2; it
does not certify understanding or complete every topic in those course modules.

## Start with a tiny example
An issue says a discount should apply at age 18. Source says `age > 18`; a proposed
patch changes it to `age >= 18`. A test checks age 18. A regression is a previously
correct case broken by that edit—for example, a wrong change also discounting 17.
A PR lets a person review the change and evidence. This is an explanatory example,
not a recorded CodePilot run or benchmark result.

Repository = versioned source folder. Issue = problem statement. Patch = proposed
source change. Test = executable check with an expected result. Commit = immutable
version identity. Branch = moving pointer to commits. Push = send commits to a
remote such as GitHub; it does not start a hosted application.

## Product, prototype, experiment, contribution
A product delivers a useful workflow. Our prototype explores feasibility on a
small supported scope. An experiment compares variants on fixed tasks and budgets.
A research contribution needs evidence beyond a functioning demo. The hypothesis
that structural context improves repair is untested. Self-authored fixtures may
be too easy (external validity); differing budgets may confound comparisons
(internal validity); passing shallow tests may poorly measure correctness
(construct validity). We must distinguish proposed, implemented and verified.

## Architecture and analogy
The API is like a reception desk, storage like a logbook, and the planned worker
like a technician. The analogy breaks because database transactions and process
failure have precise semantics that a paper logbook does not.

`HTTP request -> FastAPI handler -> SQLite check -> JSON response`

`GET /api/health` proves the process can read its initialized database. It says
nothing about Gemini credentials, Docker availability, or correct generated code.
Later: issue -> immutable checkout -> baseline -> index/retrieve -> Gemini proposal
-> policy -> independent tests -> approval -> draft PR. The model proposes;
ordinary program logic enforces limits. That distinction supports both agent-based
bug repair and behavior-preserving refactoring research.

## Walk through the actual code
- `backend/codepilot/config.py`: `Budgets` uses Pydantic fields to reject invalid
  limits. `candidates=4` violates a hard ceiling of three. Frozen values prevent
  accidental mutation after validation. This validates configuration; actual
  time/call enforcement still belongs to the future worker.
- `storage.py`: `Store.initialize` creates versioned run/event tables. A foreign
  key stops orphan events. A composite primary key prevents duplicate sequence
  numbers within a run. WAL allows readers while a writer appends; it does not
  allow unlimited concurrent writers. Connections close after short transactions.
- `api.py`: lifespan initializes storage at startup; `health` reads schema version.
  Settings are injected so tests can use temporary databases. TrustedHost rejects
  unexpected hostnames; it is not authentication. No mutation routes exist yet.
- `cli.py`: the command-line path uses the same Store as HTTP. This makes backend
  progress observable before React exists. It binds the server to loopback.

Schema setup and health use constant-size work at M0. A future event list will
scale with returned rows and should be paginated. SQLite is chosen over PostgreSQL
for one local user; explicit Python orchestration is planned over an agent framework
so state changes and failure policies remain visible.

## Commands, evidence and failure analysis
Run `uv sync --locked`, `uv run --locked pytest -q`, and
`uv run --locked codepilot health`. Exact observed results are in
`../evidence/M0-verification.md` after verification. Tests exercise real SQLite,
HTTP handlers, rejected settings, unexpected hosts and Git ignore rules. They do
not verify live AI, target isolation, a working worker, or browser UI.
Initial environment checks hit sandbox network denial; elevated read checks
confirmed GitHub authentication. Docker then genuinely lacked a running socket.
This illustrates why environment failure must not be reported as product success.

## Interview questions
Beginner: What does the current implementation do?
It starts a local API/CLI, validates settings and initializes persistent schema.
It cannot yet repair code. The broader repair pipeline is planned.

Intermediate: Why FastAPI and SQLite?
Typed request handling and a lightweight single-user database keep a prototype
inspectable. Short transactions and WAL help local access; PostgreSQL is a future
choice if concurrency or deployment requirements outgrow this scope.

Advanced: Does a successful health check establish reliability?
No. It checks a narrow invariant. Layered tests, protected evaluation, repeated
live tasks and disclosed failures are needed before stronger claims.

## Exercise and teach-back (unassessed)
Label five claims planned/implemented/verified/measured/unknown. Include “CodePilot
uses Gemini successfully” and “CodePilot rejects a candidate budget of four.”
Then run the budget rejection test and explain what it establishes.

Teach-back: Why is a patch different from a verified fix? Why doesn't pushing code
make the app live? What could still be broken when `/api/health` returns OK?

<details><summary>Exercise guidance</summary>
Gemini success remains unknown/unverified. Budget validation is implemented and
becomes verified after its test passes. Neither demonstrates a full repair.
</details>

## Learning progress

The course exercises and teach-back are not yet assessed.
