# CodePilot

A local, AI-assisted software-maintenance research prototype. **This MVP uses
scripted proposals on controlled Python fixtures; it does not claim live AI repair.**
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
No Gemini or OpenAI key is required. Then run:

```sh
./scripts/start-demo.sh
```

Open [CodePilot locally](http://127.0.0.1:8000). Keep the terminal open; Ctrl-C stops
both processes. The startup script prepares five trusted Git fixture repositories.
Select **boundary**, keep **Offline scripted demo**, and click **Start run**. After
validation, inspect **Diff**, **Checks**, **Plan**, and **Source**. Select **refactor**
for the extract-helper example. The remaining targets demonstrate failures.
Task text changes retrieval, but the offline proposal remains a fixed fixture script.

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
live Gemini verification. Live generation is excluded from the MVP at the user's
request; its experimental adapter remains in source, while the UI/API accept offline
runs only. Tree-sitter edges and smell metrics are approximate. Test success is not
proof of correctness. Browser visual verification remains pending due to the desktop
app's unavailable browser attachment; API flows and frontend compilation are tested.

The runner uses a pinned image, read-only source/root, non-root user, no network,
limited resources, and no host secrets or Docker socket. Docker itself is privileged;
keep the control plane on loopback. Runtime source, reports, database and `.env` stay
under ignored local paths. Dependencies are locked; no project license is selected.
