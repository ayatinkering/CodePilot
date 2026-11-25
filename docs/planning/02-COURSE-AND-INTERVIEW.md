# CodePilot build-along course and interview preparation

Read together with 01-PRD.md and 03-ASTRA-START-HERE.md. This is a teaching contract for the coding agent, not a claim that the learner already knows these topics.

## Teaching method required at every milestone

Teach using the actual system being built. Start with an accessible explanation, define new vocabulary, show a small concrete example, then connect it to the production code and its limitations. Avoid an unexplained wall of code or a list of buzzwords. Use small diagrams when they clarify flow.

Before implementation:
1. Explain the user problem and why this component exists.
2. Introduce prerequisites from scratch; do not assume familiarity with Git, embeddings, APIs or program analysis.
3. Draw inputs → processing → outputs and identify what can fail.
4. Compare two reasonable approaches and explain the chosen one.

After implementation:
1. Show the real files/functions and trace one real input through them.
2. Explain the important code blocks, types, data structures, algorithms and complexity. Do not narrate every import or trivial JSX line.
3. Show successful output and a failure example, including what the test does and does not establish.
4. Connect the implementation to the relevant CV statement and Sharma project.
5. Provide beginner, intermediate and advanced interview questions with answers grounded in the current code.
6. Give one small modification/exercise Ayati can perform and a way to check it.
7. Ask 2–3 teach-back questions. Record unanswered questions as unassessed, never mastered.
8. Save the full lesson and concise recap in the repository; show a readable explanation in chat.

Do not make every quiz a blocking approval. Continue independent implementation while Ayati answers. If she says she is confused, slow down on that topic and use a smaller example. Maintain a misconception log. Keep full explanations in lesson files so a long chat does not lose them.

Each lesson file contains: objectives; prerequisites; glossary; analogy and where it breaks; technical explanation; mini example; architecture decision; annotated code walkthrough; actual commands/results; failure analysis; exercises with separate solutions; interview questions; connection to the PRD; remaining limitations.

## Module 0 — What this project is, and what research means

From scratch: distinguish software product, prototype, experiment and research contribution. Explain the issue-to-patch journey using a tiny function with a wrong boundary condition. Define repository, issue, patch, test, regression and pull request.
Intermediate: explain how a working demonstration differs from evidence across multiple tasks; feasibility versus reliability; user benefit versus benchmark score.
Advanced: construct, internal and external validity; why self-authored tasks and familiar repositories limit generalization; hypothesis versus observation.
Exercise: write five statements about CodePilot and label each planned, implemented, verified, measured or unknown.
Interview: 'What problem are you solving?' 'What is the research contribution?' 'What have you personally done?'
Deliverable: project pitch and honest capability ledger with no completed features at the outset.

## Module 1 — Git, GitHub and reproducible development

From scratch: working tree, staging, commit, branch, remote, push, clone, diff, merge and PR. Git is version control; GitHub hosts repositories and collaboration features. Explain why a GitHub repository is not a running web application.
Intermediate: immutable commit identity, base/head, clean worktrees, remote tracking, branch conflicts, .gitignore, secrets, lockfiles and dependency reproducibility.
Advanced: optimistic concurrency, stale analysis, idempotent publication, retries after uncertain network responses; why rebasing/force-pushing can invalidate review references.
Exercise: change one fixture, inspect diff, commit to a practice branch, find the commit SHA and explain exactly what was pushed.
Interview: 'Why analyze an exact commit?' 'What happens when main changes before the PR?' 'Why not directly edit the user's checkout?'
Deliverable: contribution history and a diagram distinguishing development commits from CodePilot-generated PRs.

## Module 2 — Python, APIs, backend architecture and persistence

From scratch: functions, modules, type hints, exceptions, JSON, HTTP requests/responses, REST routes, frontend/backend separation and environment variables.
Intermediate: Pydantic validation, service boundaries, dependency injection, SQLite rows/keys/indexes, transactions, migrations and artifact storage. Explain async I/O versus CPU work and processes versus threads.
Advanced: why async functions do not automatically make heavy jobs nonblocking; why request lifecycle and worker lifecycle differ; job ownership, state machines, failure recovery, CORS and local API access boundaries.
Exercise: add a validated configuration field, persist it per run and show an invalid request response.
Interview: 'Why FastAPI?' 'Why SQLite rather than PostgreSQL?' 'What happens if the server restarts?' 'How do you avoid duplicate job execution?'
Deliverable: actual API/data-model walkthrough and ADR for the single-user modular-monolith architecture.

## Module 3 — Repository acquisition and execution lifecycle

From scratch: source files, dependencies, imports, test configuration, commit snapshots, trusted versus untrusted input.
Intermediate: canonical paths, exclusions, size limits, clone behavior, hooks/submodules, artifact directories, baseline state and job events.
Advanced: time-of-check/time-of-use mistakes, symlink escapes, uncontrolled downloads, internal network fetch risks and why tests themselves execute arbitrary code.
Exercise: submit a path with traversal, an oversized source file and a repository containing a symlink; inspect the rejection or exclusion evidence.
Interview: 'What languages and repositories are actually supported?' 'How is the original repository protected?' 'What if there are no tests?'
Deliverable: supported-target contract with demonstrated edge cases.

## Module 4 — Parsing, CSTs, ASTs and program analysis

From scratch: lexical tokens versus syntax; parsing source into a tree; Tree-sitter's concrete syntax tree and application-derived AST-like symbols. Walk through a ten-line Python function.
Intermediate: nodes, queries, source spans, scopes, functions/classes/imports, call expressions, alias resolution, parse errors, incremental parsing and symbol graphs.
Advanced: distinguish syntax tree, call graph, control-flow graph and data-flow graph. Explain static versus dynamic analysis, soundness versus completeness, approximate resolution and dynamic dispatch. Teach why seeing obj.run() does not determine every possible target method.
Code-quality concepts: cohesion, coupling, single responsibility, Long Method, parameter count, nesting and metric thresholds. A smell is a contextual signal; avoid arbitrary 'clean code' certainty.
Exercise: create nested functions, an alias and a dynamic call; compare source, parse tree, extracted symbols and unresolved edges. Add one simple structural finding and test it.
Interview: 'Why Tree-sitter rather than regex or Python ast?' 'Do you build a real call graph?' 'What does your smell detector actually measure?'
Deliverable: tree example, graph limitations and fixture-backed extraction guide.

## Module 5 — Embeddings, semantic search and code RAG

From scratch: vectors as numerical representations; embeddings are learned representations, not hashes or compressed source that can be perfectly decoded. Compare exact word matching with meaning-based similarity.
Intermediate: tokenize/chunk/embed/store/query; cosine similarity dot(a,b)/(|a||b|); normalized vectors; function-aware chunks; metadata; lexical search; rank fusion; top-k; context selection.
Advanced: retrieval recall and relevance; reciprocal-rank fusion 1/(k+rank); model mismatch; stale vectors; cache invalidation; structural expansion; reranking; context budgets; 'lost in the middle'; exact search O(Nd) versus approximate-nearest-neighbor trade-offs. Similarity scores are not probabilities of correctness.
Explain RAG versus fine-tuning: retrieval supplies external context during inference; fine-tuning changes parameters. The original RAG literature and this project's retrieval pipeline need not use identical training mechanisms.
Exercise: query the same code by symbol and by behavior; inspect lexical/semantic contributions. Rename/delete a function and prove stale evidence is removed. Compare retrieval with and without related tests.
Interview: 'Which embedding model and dimension?' 'Why this chunk size?' 'How are dependencies represented?' 'How do embeddings update after edits?' 'Why no vector database initially?'
Deliverable: actual model identity/configuration, example retrieval traces and incremental-update experiment.

## Module 6 — LLM fundamentals, prompting and typed generation

From scratch: AI → ML → deep learning → language modeling; training versus inference; tokens, embeddings, next-token prediction and why fluent output can be wrong.
Intermediate: transformer attention using Q/K/V and softmax(QKᵀ/sqrt(d))V; positional information; causal masking; feed-forward layers; context limits; sampling temperature and top-p. Explain at a conceptual level, not as architecture claims about an undocumented proprietary model.
Training overview: pretraining, supervised fine-tuning, preference/reward alignment; LoRA as parameter-efficient adaptation; what this project does NOT train. Inference-time repair does not update weights and is not reinforcement learning.
Engineering: prompt roles, retrieved evidence, schema validation, bounded retries, token accounting, provider errors, model configuration and fake versus live adapters. Structured output helps format reliability, not factual correctness.
Advanced: tool calling as structured action proposals; policy enforcement outside the model; prompt injection in issue/code text; nondeterminism even with low temperature; correlated generator/critic mistakes; leakage and pretraining contamination.
Exercise: deliberately return invalid JSON from the fake provider; inspect recovery. Give a task without sufficient evidence and inspect abstention. Trace the actual sanitized request sent to the live model.
Interview: 'Which model did you use and why?' 'Does RAG eliminate hallucinations?' 'Why not fine-tune?' 'What happens on a provider outage?'
Deliverable: exact model settings, prompt/schema walkthrough and live-call evidence without secrets.

## Module 7 — Agents, tools, planning and patches

From scratch: workflow versus agent; observe → choose action → execute → inspect feedback. Distinguish an LLM, its orchestrator, tools and stored state.
Intermediate: explicit state transitions, typed plans, tool schemas, plan evidence, bounded tools, patch structure, preimage hashes, exact edits and unified diffs.
Advanced: why a deterministic outer workflow can contain adaptive model decisions; single-agent versus multi-agent costs; framework versus handwritten orchestration; model self-assessment limitations; rollback and candidate isolation; policy checks before and after application.
Exercise: request an unauthorized file edit, duplicate an edit preimage and change the file after planning. Explain why each is rejected. Apply a valid small patch and inspect resulting diff.
Interview: 'Why is CodePilot agentic?' 'Why no LangGraph/multi-agent setup initially?' 'How are patches applied?' 'Can it edit tests or CI?' 'What stops an endless loop?'
Deliverable: real state-transition trace and patch-policy rationale.

## Module 8 — Testing, oracles and behavioral correctness

From scratch: test inputs, expected results, assertions, unit/integration/end-to-end tests; bug versus regression; pytest collection and execution.
Intermediate: test fixtures, mocking boundaries, parameterized tests, baseline failures, generated tests and issue reproduction. Explain why success exit status with zero tests is insufficient.
Advanced: oracle problem; property-based testing; differential and metamorphic testing; mutation testing; test adequacy versus coverage; flaky tests; independent hidden evaluators; leakage from oracle answers into generation context.
Explain that tests establish behavior on selected cases. They do not prove arbitrary program equivalence. For a bug fix, desired behavior intentionally changes; for refactoring it should be preserved.
Exercise: produce a wrong patch that passes shallow tests, then write an independent test that detects it. Show a generated test that passes both baseline and candidate and explain what it establishes.
Interview: 'How do you know the patch is correct?' 'What if the baseline already fails?' 'Can the same model write the patch and its tests?' 'Why is coverage not correctness?'
Deliverable: test-origin matrix and validation evidence with limitations.

## Module 9 — Containers, isolation, repair and failure analysis

From scratch: process, filesystem, environment variables, container image versus container, host versus execution environment; Docker versus a VM.
Intermediate: mounted directories, users, read-only root, network restrictions, CPU/memory/process limits, timeout/cancellation, clean environments and locked dependencies.
Advanced: shared-kernel limitations, Docker daemon privilege, rootless mode, seccomp, privilege escalation surfaces, dependency installation as code execution and avoiding provider credentials inside test containers. Do not equate a Dockerfile with sandboxing.
Repair: transform structured failures into bounded feedback; classify source defect/environment defect/policy rejection/provider error; detect repeated patches and stop. Explain wall-clock/call/token budgets.
Exercise: timeout a nonterminating fixture, attempt network access and inspect available environment variables without exposing host secrets. Force repeated failed candidates and inspect termination.
Interview: 'How is execution isolated?' 'What happens without Docker?' 'How many repair attempts?' 'When does the agent give up?'
Deliverable: threat model, failure taxonomy and actual boundary-test results.

## Module 10 — React, streaming and observability

From scratch: component, prop, state, event handler, API request and rendering. Explain how the UI differs from the worker doing the work.
Intermediate: typed API clients, state derived from persisted runs, SSE versus polling/WebSockets, event IDs, reconnect replay, diff views and test-result presentation.
Advanced: stale UI state, duplicate events, cancellation races, XSS from repository content, sanitized logs, timing/usage metrics and traceability. Explain why action summaries are not access to hidden model reasoning.
Exercise: refresh during a run, disconnect/reconnect and cancel mid-test. Trace one event from worker to database to UI.
Interview: 'How do you visualize trajectories?' 'What survives a refresh?' 'Why SSE?' 'Which data must never reach the browser?'
Deliverable: browser walkthrough and real screenshots, including a failure state.

## Module 11 — GitHub issues, authentication and PR automation

From scratch: issue versus PR, API endpoint, token, read versus write permission and draft PR.
Intermediate: repository authorization, issue ingestion, branch creation, push, PR creation, rate limits, credential handling and patch approval digest.
Advanced: idempotency and uncertain network responses; stale base SHA; permission-denied handling; installation token lifecycle if using a GitHub App. Explain webhooks, event signatures, queues and bot-event loops as future/implemented status dictates.
Exercise: publish one approved patch to an authorized target, retry the action and confirm one PR. Move the base and confirm stale validation is surfaced.
Interview: 'What permissions does the app need?' 'What if GitHub times out after creating the PR?' 'Why draft PRs?' 'Is it actually an installed GitHub App?'
Deliverable: actual issue/branch/PR links and a clean explanation of implemented auth versus planned integration.

## Module 12 — Refactoring and maintainability research

From scratch: structural change versus behavior change; Extract Method/Helper; naming and responsibilities; cohesion/coupling and technical debt.
Intermediate: candidate detection versus patch generation; local variables, parameters, returns, closures, exception order, mutation, resources and async behavior. Walk through a small extraction and identify invariants.
Advanced: deterministic refactoring engines versus LLM generation; metric gaming; developer judgment; semantics versus syntax; preservation tests and uncertainty; how adding abstractions can worsen comprehension.
Exercise: refactor a suitable function, then construct a similar-looking extraction that changes an exception or side effect; observe rejection. Find a case where doing nothing is better.
Interview: 'How do you detect a need to refactor?' 'Why use an LLM?' 'How do you measure improvement?' 'Why not an IDE refactoring tool?' 'What cannot be guaranteed?'
Deliverable: two concrete examples tied to Sharma's refactoring project and a paper reading note.

## Module 13 — Evaluation, baselines and reproducibility

From scratch: benchmark task, label, baseline, metric, denominator and failure category.
Intermediate: controlled comparisons, ablations, held-out data, repository-level splits, leakage, fixed budgets and reproducible configuration. Explain accuracy/precision/recall/F1 only where suitable labels exist.
Advanced: data contamination, sampling variance, confidence intervals, compute confounds, selection bias, validity threats, quality/cost/latency trade-offs and why a tiny curated benchmark is not a universal success rate.
Exercise: compare two retrieval variants on identical tasks; report every attempt. Calculate success rate from the raw denominator and explain why negative tasks need separate abstention metrics.
Interview: 'What percentage of tasks did it solve?' 'What failed?' 'What is your baseline?' 'Is the improvement statistically meaningful?' 'Could the model have seen these tasks?'
Deliverable: generated report, raw results and a short limitations section. No invented numbers.

## Module 14 — Reading research and discussing Professor Sharma's work

Read abstracts, methods and threats to validity for selected papers; do not pretend to have read entire papers after a skim.
- Grounding Generative AI in Software Engineering: Are We There Yet? https://tusharma.in/preprints/SANER2026_SENAI.pdf
- Reinforcement Learning vs Supervised Learning: A tug of war to generate refactored code accurately. https://tusharma.in/preprints/EASE2025_RL_Refactoring.pdf
- DPy: Code Smells Detection Tool for Python. https://tusharma.in/preprints/MSR2025_DPy.pdf
- Lab overview: https://web.cs.dal.ca/~tushar/smart/

For each: problem, approach, evaluation, one limitation, one connection to the actual CodePilot implementation. Do not claim our inference loop reproduces PPO training. Do not claim our simple metrics reproduce DPy.
Exercise: propose one controlled experiment and one reason it might fail.
Interview: 'Why this lab?' 'How does your project relate to mine?' 'What would you do in the first two weeks?' 'What is the research question beyond building an app?'
Deliverable: evidence-based research-fit note and realistic 12-week extension plan.

## Module 15 — Interview defense and personal ownership

Prepare 30-second, 90-second and five-minute explanations. Each includes problem, implemented architecture, personal contribution, actual evidence, one failure and a limitation.
Do not use a memorized ideal architecture if the code differs. For each technical claim, link a code path and an observed result. Distinguish understanding from merely having working files.
Exercise: Ayati implements one small change herself, explains the diff, runs its test and describes the outcome. Then conduct a mock interview with follow-up questions rather than only rehearsed prompts.
Deliverables: project-defense.md, factsheet.md, known-limitations.md and an updated honest CV bullet set appropriate to the actual completion level.

## Required knowledge ledger

Use columns: topic | explained | exercised | teach-back status | misconception | next action | evidence.
States: unintroduced, explained, practiced, demonstrated, needs_review. Only demonstrated after an actual answer/exercise; no automatic mastery checkmarks.

## Interview question bank with expected answer elements

1. What does CodePilot do? Trace a real task through actual modules.
2. What does it not support? Name language/build/trust limits.
3. Which model and embedding model? Exact IDs/revisions from configuration, not guesses.
4. What is indexed? Symbols/chunks/metadata and exclusions.
5. How is context selected? Actual fusion, neighbor expansion, budget and evidence.
6. How are updates handled? Hashes, snapshots, deletions and model-version invalidation.
7. Does Tree-sitter understand semantics? Distinguish parsing and approximate analysis.
8. Is your call graph complete? State unresolved/dynamic cases.
9. What makes it an agent? Adaptive actions/feedback inside bounded orchestration.
10. Why not several agents? Discuss a measured need versus extra complexity.
11. What did you train? State no training if only inference is implemented.
12. Is retrying reinforcement learning? No weight update; explain the difference.
13. How does patch application work? Preconditions, exact edits, diff inspection and rollback.
14. Can it edit tests? Protected originals, separate proposed tests, explicit policy.
15. What if tests already fail? Baseline classification and publication rule.
16. What if there are no tests? Insufficient validation, not automatic success.
17. How are tests generated? From specification/context; explain oracle limitations.
18. Can it game its tests? Independent evaluator and protected checks; residual limitations.
19. How do you preserve behavior? Layered evidence, no universal proof.
20. Why Docker? Reproducibility and restrictions, shared-kernel limitations.
21. Where are API keys? Trusted backend only; absent from target execution and logs.
22. What if a README tells it to leak secrets? Untrusted data and external tool policy.
23. Why SQLite? Single-user simplicity; concurrency and scaling limits.
24. Why SSE? Server-to-client event delivery, persistence and replay.
25. What if the worker crashes? Actual interrupted/retry behavior, not fictional durable resume.
26. What if the base branch advances? Stale result/revalidation.
27. What if PR creation times out? Reconcile deterministic markers before retry.
28. How many attempts and how much cost? Recorded limits and observed usage.
29. What is your success rate? Raw live-task denominator and limitations.
30. What did an ablation show? Actual result, including no improvement.
31. What was your hardest bug? Real development log with evidence.
32. Why refactor instead of fix a bug? Task objective and invariants differ.
33. Can lower complexity mean worse design? Explain metric gaming with an example.
34. Why Professor Sharma? Specific research connection you have read and understood.
35. What would you improve next? One failure-driven change and how to evaluate it.
36. What did you personally implement? An accurate account of your contributions.
37. What was already complete when you applied? Truthful timeline; do not imply later work existed earlier.

## Final one-page factsheet template

- Build status and verified date:
- Supported targets:
- Generation provider/model/settings:
- Embedding model/revision/dimension:
- Chunk and retrieval design:
- Structural analysis and limitations:
- Patch format and allowed paths:
- Baseline/test policy:
- Maximum attempts/calls/time/tokens:
- Runner restrictions and trust scope:
- Actual tasks attempted/resolved/failed:
- Real PR evidence:
- One failed case and lesson:
- My actual contributions:
- What remains planned:

Fill from repository evidence only. A good answer to an unknown question is: 'I have not implemented that; here is my current understanding and how I would test it.'
