import asyncio
import json
import secrets
import subprocess
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field
from starlette.middleware.trustedhost import TrustedHostMiddleware

from codepilot.acquisition import git
from codepilot.config import Budgets, Settings
from codepilot.demo import ROOT, registry
from codepilot.github import GitHubError, import_issue, publish
from codepilot.jobs import Jobs
from codepilot.providers import redact
from codepilot.storage import Store


class RunInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    repository_id: str
    task: str = Field(min_length=1, max_length=10000)
    mode: Literal["repair", "refactor"] = "repair"
    provider: Literal["offline", "gemini"] = "offline"
    issue_number: int | None = Field(default=None, ge=1)
    base_sha: str | None = Field(default=None, pattern=r"^[0-9a-f]{40}$")
    budgets: Budgets = Field(default_factory=Budgets)


class Approval(BaseModel):
    model_config = ConfigDict(extra="forbid")
    base_sha: str = Field(pattern=r"^[0-9a-f]{40}$")
    patch_digest: str = Field(pattern=r"^[0-9a-f]{64}$")


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    store = Store(settings.data_dir / "codepilot.sqlite3")
    jobs = Jobs(store)
    session_token = secrets.token_urlsafe(32)

    @asynccontextmanager
    async def lifespan(app):
        store.initialize()
        yield

    app = FastAPI(title="CodePilot", version="0.2.0", lifespan=lifespan)
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "testserver"]
    )
    app.state.store = store
    app.state.settings = settings

    @app.middleware("http")
    async def local_boundary(request, call_next):
        if request.url.path.startswith("/api/"):
            if request.method not in {"GET", "HEAD", "OPTIONS"}:
                expected = f"{request.url.scheme}://{request.headers.get('host', '')}"
                if request.headers.get("origin") != expected:
                    return Response("Same-origin local request required", status_code=403)
            if request.url.path not in {
                "/api/health",
                "/api/session",
            } and not secrets.compare_digest(
                request.cookies.get("codepilot_session", ""), session_token
            ):
                return Response("Open CodePilot locally to start a session", status_code=401)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.post("/api/session")
    def session(response: Response):
        response.set_cookie("codepilot_session", session_token, httponly=True, samesite="strict")
        return {"status": "local_session_ready"}

    @app.get("/api/health")
    def health():
        return {"status": "ok", "schema_version": store.health(), "release": "foundation"}

    @app.get("/api/capabilities")
    def capabilities():
        return {
            "provider": settings.provider,
            "model": settings.model or None,
            "gemini_key_configured": bool(settings.gemini_api_key.get_secret_value()),
            "runner_configured": bool(settings.runner_image),
            "embedding_model_prepared": (settings.data_dir / "models").exists(),
            "live_generation_verified": any(
                r["state"] in {"ready_for_review", "published"}
                and json.loads(r["provider_json"]).get("provider") == "gemini"
                and json.loads(r["provider_json"]).get("model") == settings.model
                for r in jobs.list()
            ),
            "supported_targets": ["Controlled Python fixtures; local single-user MVP"],
            "repair_pipeline_available": True,
            "github_app_webhooks": False,
        }

    def lookup(run_id):
        try:
            return jobs.get(run_id)
        except KeyError:
            raise HTTPException(404, "Run not found") from None

    def directory(run_id):
        lookup(run_id)
        return settings.data_dir / "runs" / run_id

    @app.get("/api/repositories")
    def repositories():
        return list(registry(settings.data_dir).values())

    @app.post("/api/runs", status_code=201)
    def submit(body: RunInput):
        if body.provider == "gemini" and (
            not settings.gemini_api_key.get_secret_value() or not settings.model
        ):
            raise HTTPException(
                400, "Configure Gemini key and model locally before selecting live generation"
            )
        entry = registry(settings.data_dir).get(body.repository_id)
        if not entry or not entry.get("trusted"):
            raise HTTPException(400, "Choose a registered trusted target")
        if body.mode != entry["mode"]:
            raise HTTPException(400, "Task type must match the controlled fixture")
        try:
            sha = (
                git(
                    Path(entry["path"]),
                    "rev-parse",
                    "--verify",
                    f"{body.base_sha or 'HEAD'}^{{commit}}",
                )
                .decode()
                .strip()
            )
        except (subprocess.SubprocessError, OSError):
            raise HTTPException(400, "Commit is not available in the registered fixture") from None
        task_text = redact(body.task)
        key = settings.gemini_api_key.get_secret_value()
        if key:
            task_text = task_text.replace(key, "[REDACTED]")
        run = jobs.submit(
            {
                "repository": entry["path"],
                "repository_id": body.repository_id,
                "text": task_text,
                "mode": body.mode,
                "issue_url": f"https://github.com/{settings.github_repo}/issues/{body.issue_number}"
                if body.issue_number
                else None,
            },
            sha,
            body.budgets,
            {
                "provider": body.provider,
                "model": settings.model if body.provider == "gemini" else "scripted-demo",
            },
        )
        return {"id": run}

    @app.get("/api/issues/{number}")
    def issue(number: int):
        if number < 1:
            raise HTTPException(400, "Invalid issue number")
        try:
            return import_issue(settings, number)
        except GitHubError as exc:
            raise HTTPException(502, str(exc)) from None
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from None

    @app.post("/api/runs/{run_id}/publish")
    def publication(run_id: str, body: Approval):
        lookup(run_id)
        try:
            return publish(jobs, settings, run_id, body.base_sha, body.patch_digest)
        except GitHubError as exc:
            raise HTTPException(502, str(exc)) from None
        except (ValueError, KeyError, OSError) as exc:
            raise HTTPException(
                409, str(exc) if isinstance(exc, ValueError) else "Publication unavailable"
            ) from None

    @app.get("/api/runs")
    def runs():
        return jobs.list()

    @app.get("/api/runs/{run_id}")
    def detail(run_id: str):
        run = lookup(run_id)
        root = directory(run_id)
        artifacts = {}
        for name in [
            "result.json",
            "baseline-report.json",
            "snapshot.json",
            "index.json",
            "publication.json",
        ]:
            path = root / name
            if path.exists():
                artifacts[name] = json.loads(path.read_text())
        return {"run": run, "events": jobs.events(run_id), "artifacts": artifacts}

    @app.post("/api/runs/{run_id}/cancel")
    def cancel(run_id: str):
        lookup(run_id)
        try:
            jobs.transition(run_id, "cancelled", "operator_cancelled")
        except ValueError:
            raise HTTPException(409, "This run can no longer be cancelled") from None
        return {"state": "cancelled"}

    @app.post("/api/runs/{run_id}/retry", status_code=201)
    def retry(run_id: str):
        run = lookup(run_id)
        if run["state"] not in {"failed", "abstained", "cancelled", "interrupted"}:
            raise HTTPException(409, "Retry requires a stopped run")
        return {
            "id": jobs.submit(
                json.loads(run["task_json"]),
                run["base_sha"],
                Budgets.model_validate_json(run["budgets_json"]),
                json.loads(run["provider_json"]),
            )
        }

    @app.get("/api/runs/{run_id}/artifacts/{name}")
    def artifact(run_id: str, name: str):
        root = directory(run_id)
        allowed = {"result.json", "baseline-report.json", "index.json", "snapshot.json"} | {
            f"candidate-{i}.diff" for i in range(3)
        }
        if name not in allowed or not (root / name).is_file():
            raise HTTPException(404, "Artifact not found")
        return FileResponse(root / name, filename=name)

    @app.get("/api/runs/{run_id}/events")
    async def events(run_id: str, request: Request, after: int = 0):
        lookup(run_id)
        try:
            cursor = max(after, int(request.headers.get("last-event-id", "0")))
        except ValueError:
            raise HTTPException(400, "Invalid event cursor") from None

        async def stream():
            nonlocal cursor
            while not await request.is_disconnected():
                for event in jobs.events(run_id, cursor):
                    cursor = event["sequence"]
                    yield f"id: {cursor}\ndata: {json.dumps(event)}\n\n"
                yield ": heartbeat\n\n"
                await asyncio.sleep(1)

        return StreamingResponse(stream(), media_type="text/event-stream")

    frontend = ROOT / "frontend/dist"
    if frontend.exists():
        app.mount("/", StaticFiles(directory=frontend, html=True), name="frontend")
    return app
