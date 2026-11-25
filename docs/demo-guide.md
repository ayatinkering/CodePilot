# Five-minute professor demonstration

Run `./scripts/start-demo.sh` from the project root and open http://127.0.0.1:8000.
Live Gemini requires the local key and model configured in `.env`; offline mode needs no key. Allow about a minute for each run; actual timing
depends on Docker startup and the machine.

1. Say the scope first: "This is a new, AI-assisted local prototype. For the live demo,
   Gemini generates a plan and edit; independent code validates it before review."
2. Choose **Live Gemini** and run the **boundary** fixture. Show its pinned base commit and retrieved source.
   The original tests pass, but the protected evaluator reproduces the age-18 bug.
3. Show the diff (`> 18` becomes `>= 18`). Open Checks: original tests, independent
   evaluator, and the auxiliary generated test are separately recorded. Explain
   that the evaluator was not provided to the generator.
4. Run **refactor**. Explain the helper extraction and show the before/after target
   function lines. Its independent test compares behavior across curated inputs.
5. Show a **baseline_failed** or **zero_tests** run. CodePilot stops instead of
   claiming success. The evaluation report also includes an incorrect candidate,
   an illegal test-file edit, and a second-attempt repair.
6. Open [real Gemini draft PR #4](https://github.com/ayatinkering/CodePilot/pull/4)
   linked to [issue #2](https://github.com/ayatinkering/CodePilot/issues/2). It targets
   only `codex/demo-fixture`, not implementation/main. The separate offline PR #3 also verified that repeated approval returns the same PR. Leave it draft and unmerged.

## A truthful 30-second introduction

"I am building CodePilot as a local software-maintenance research prototype with
AI coding assistance. It snapshots a Python target, parses it with Tree-sitter,
retrieves code with local embeddings, and validates bounded candidate edits inside
Docker before review. Live Gemini generates new candidates from the task and source. I also keep a
separate scripted test suite, including wrong candidates, to test the control flow."

## A truthful 90-second explanation

"The central distinction is proposing a change versus trusting it. I preserve the
original snapshot and existing tests, validate exact edit preimages and budgets,
and use independent checks that generation cannot see. The refactoring example
must preserve tested behavior as well as reduce the target function's size. The
UI shows each attempt and its evidence; GitHub publication binds approval to the
base SHA and patch digest. There are 12 scripted acceptance scenarios and two successful live Gemini fixture
runs, not a broad LLM benchmark. The implementation was AI-assisted; I am learning the
architecture and cannot claim independent ownership of every implementation detail."

## Questions to practice

- Why can old tests pass before the bug is fixed? They omit the failing boundary.
- Why embeddings? They retrieve semantically related text beyond exact tokens.
  This implementation combines semantic and lexical ranks; it does not train a model.
- Why Tree-sitter? It locates syntax and symbols without executing target source.
  Its reported call edges are approximate, not a complete call graph.
- Why Docker? It limits target execution. It is not proof against all hostile code,
  and this app accepts trusted fixtures only.
- Does 12/12 mean 100% repair success? No: it means all scripted cases produced the
  expected acceptance or rejection. Some intentionally failed.
- What remains? Broader projects, stronger evaluations, precise
  impact analysis, production security, and visual browser verification.

Practice by tracing `api.py → jobs.py → worker.py → pipeline.py → runner.py` and then
`github.py`. Explain a failed run using its saved report. Understanding has not been
assessed; do not memorize claims that you cannot explain or imply historical work.

## Live evidence

See `docs/evidence/live-generation.json`: real Gemini 3.5 Flash generated a repair
and a distinct helper extraction. Both passed original and protected evaluator tests
in Docker. Four calls used 7,236 reported tokens; setup probes are separate.
The live run is selectable in history and labeled Live Gemini. A future request can
still fail due to provider availability or quota; never promise guaranteed success.
