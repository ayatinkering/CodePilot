# CodePilot

A local, AI-assisted software-maintenance research prototype. **This MVP supports live Gemini generation and a separately labeled offline scripted mode
on controlled Python fixtures.**
Two live Gemini fixture runs (repair and refactoring) passed independent Docker
validation. [Raw live evidence](docs/evidence/live-generation.json) is separate from
the scripted acceptance suite.

Parsing, local embeddings, hybrid retrieval, Docker validation, the review API/UI,
GitHub issue import, and approved draft PR publication are implemented.

## Start the demo

Requirements: Linux, Git, Python 3.12, uv, Node.js 22.12+, and running Docker
Engine/Desktop. GitHub CLI authentication is only needed for issue/PR operations.
Initial installation/model/image preparation needs network access; offline runs do not.

```sh
git clone --branch codex/codepilot-build https://github.com/ayatinkering/CodePilot.git
cd CodePilot
uv sync --locked
npm ci --prefix frontend
npm run build --prefix frontend
uv run --locked codepilot prepare-model
docker build -t codepilot-runner:dev runner
# Copy only on first setup; do not overwrite an existing .env.
cp -n .env.example .env
docker image inspect codepilot-runner:dev --format '{{.Id}}'
```

Put the printed `sha256:...` value after `CODEPILOT_RUNNER_IMAGE=` in `.env`.
No API key is required for offline mode. For live generation, set `GEMINI_API_KEY`
in the ignored `.env` and set `CODEPILOT_MODEL=gemini-3.5-flash`. Never paste keys
in chat or commit them. Live mode sends selected task/source to Google and uses
API quota. Then run:

```sh
./scripts/start-demo.sh
```

Open [CodePilot locally](http://127.0.0.1:8000). Keep the terminal open; Ctrl-C stops
both processes. The startup script prepares five trusted Git fixture repositories.
Select **boundary**, choose **Live Gemini** (or **Offline scripted demo**), and click
**Start run**. Live mode generates a new plan, patch and auxiliary test from the task. After
validation, inspect **Diff**, **Checks**, **Plan**, and **Source**. Select **refactor**
for the extract-helper example. The remaining targets demonstrate failures.
In offline mode, task text changes retrieval, but the proposal remains a fixed fixture
script. Live mode never falls back to that script: outages, quotas, malformed output
and validation failures are recorded as stopped runs. Use Retry after resolving a
provider problem; it keeps the original base and model. In-flight calls are bounded
to 60 seconds, so cancellation may wait for the current request to finish.

If port 8000 or the worker lock is occupied, stop the previous CodePilot process.
Do not run the evaluation command while the worker is running. An interrupted run
is recorded on worker restart; retry creates a new run at the same base commit.

## GitHub demonstration

The implementation is on `codex/codepilot-build`, with [draft implementation PR #1](https://github.com/ayatinkering/CodePilot/pull/1).
A separate `codex/demo-fixture` branch contains only the synthetic discount target.
[Controlled issue #2](https://github.com/ayatinkering/CodePilot/issues/2) can be imported
using the dashboard's issue-number field. The local operator has opted this fixture
into publication; a new installation defaults to publication disabled.

For another installation, explicitly bind the registered boundary fixture in ignored
`.codepilot/repositories.json`: `publication_allowed: true`, `github_repo:
"ayatinkering/CodePilot"`, `base_branch: "codex/demo-fixture"`. The local fixture's
base SHA must equal that remote branch. A fresh generated fixture has a different
commit SHA: clone the dedicated branch into a new trusted target directory and set
that registry entry's absolute `path` to the clone. Do not repoint it to main.
Authentication stays in the host `gh` configuration, never in target containers.

Review the exact patch and evidence, check the approval box, then create a **draft**
PR. Changed bases or modified candidates are rejected. Ambiguous publication can be
reconciled by approving the same digest again. No force push or automatic merge.

## Verify

```sh
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked pytest -q
CODEPILOT_TEST_RUNNER_IMAGE=$(docker image inspect codepilot-runner:dev --format '{{.Id}}') \
  uv run --locked pytest -q
# Stop the worker first:
uv run --locked codepilot evaluate
```

The evaluation records **12 scripted acceptance scenarios over two synthetic source
fixtures**, including expected rejections. It is not an LLM benchmark, and the A/B/C
retrieval cases do not establish quality improvements because generation is fixed.
See [raw results and summary](evaluation/results/summary.md),
[capability ledger](docs/evidence/capabilities.md), and [demo/interview guide](docs/demo-guide.md).

## Boundaries

Local single-user, trusted Python fixtures only. No arbitrary repository execution,
remote GitHub App/webhooks, public hosting, automatic merging, model training, or
unrestricted AI execution. Live generation uses a pinned per-run model, bounded calls
and tokens, typed JSON output, protected tests and human review. Tree-sitter edges and smell metrics are approximate. Test success is not
proof of correctness. Browser visual verification remains pending due to the desktop
app's unavailable browser attachment; API flows and frontend compilation are tested.

The runner uses a pinned image, read-only source/root, non-root user, no network,
limited resources, and no host secrets or Docker socket. Docker itself is privileged;
keep the control plane on loopback. Runtime source, reports, database and `.env` stay
under ignored local paths. Dependencies are locked; no project license is selected.
