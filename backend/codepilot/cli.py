import argparse
import json
import os
from pathlib import Path

from codepilot.acquisition import git
from codepilot.config import Budgets, Settings
from codepilot.jobs import Jobs
from codepilot.storage import Store


def main():
    parser = argparse.ArgumentParser(description="CodePilot local control plane")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ["health", "serve", "worker", "plan-smoke"]:
        commands.add_parser(name)
    submit = commands.add_parser("submit")
    submit.add_argument("repository", type=Path)
    submit.add_argument("task")
    for name in ["status", "cancel", "index"]:
        command = commands.add_parser(name)
        command.add_argument("run_id")
    args = parser.parse_args()
    settings = Settings()
    if args.command == "plan-smoke":
        from codepilot.providers import (
            Evidence,
            GeminiProvider,
            OfflineProvider,
            ProviderFailure,
            plan_task,
        )

        provider = None
        try:
            provider = (
                OfflineProvider()
                if settings.provider == "offline"
                else GeminiProvider(settings.gemini_api_key.get_secret_value(), settings.model)
            )
            print(
                json.dumps(
                    plan_task(
                        provider,
                        "Apply the discount starting at age 18, including 18.",
                        [
                            Evidence(
                                id="example:1",
                                path="src/example.py",
                                text="def discount(age): return age > 18",
                            )
                        ],
                        {"src/example.py"},
                    ),
                    indent=2,
                )
            )
        except ProviderFailure as exc:
            parser.exit(2, str(exc) + "\n")
        finally:
            if isinstance(provider, GeminiProvider):
                provider.close()
        return
    if args.command == "serve":
        import uvicorn

        from codepilot.api import create_app

        uvicorn.run(create_app(settings), host="127.0.0.1", port=8000)
        return
    if args.command == "worker":
        from codepilot.worker import main as worker_main

        worker_main()
        return
    store = Store(settings.data_dir / "codepilot.sqlite3")
    store.initialize()
    jobs = Jobs(store)
    if args.command == "health":
        print(json.dumps({"status": "ok", "schema_version": store.health()}))
    elif args.command == "submit":
        repo = args.repository.absolute()
        allowed = [
            Path(p).resolve()
            for p in os.environ.get("CODEPILOT_ALLOWED_REPOS", "").split(os.pathsep)
            if p
        ]
        if repo != repo.resolve() or repo not in allowed or ".." in repo.parts:
            parser.error("Repository must be explicitly allowlisted and have no symlink/traversal")
        if not 1 <= len(args.task) <= 10000:
            parser.error("Task must contain 1–10000 characters")
        sha = git(repo, "rev-parse", "--verify", "HEAD^{commit}").decode().strip()
        print(
            jobs.submit(
                {"repository": str(repo), "text": args.task, "mode": "repair"},
                sha,
                Budgets(),
                {"provider": settings.provider, "model": settings.model},
            )
        )
    elif args.command == "cancel":
        jobs.transition(args.run_id, "cancelled", "operator_cancelled")
        print(json.dumps({"state": "cancelled"}))
    elif args.command == "index":
        from codepilot.indexing import findings, index_snapshot

        run = jobs.get(args.run_id)
        directory = settings.data_dir / "runs" / run["id"]
        manifest = json.loads((directory / "snapshot.json").read_text())
        result = index_snapshot(directory / "baseline", manifest)
        result["findings"] = findings(result)
        (directory / "index.json").write_text(json.dumps(result, indent=2))
        print(json.dumps(result, indent=2))
    else:
        print(
            json.dumps({"run": jobs.get(args.run_id), "events": jobs.events(args.run_id)}, indent=2)
        )
