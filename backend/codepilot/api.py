from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.trustedhost import TrustedHostMiddleware

from codepilot.config import Settings
from codepilot.storage import Store


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    store = Store(settings.data_dir / "codepilot.sqlite3")

    @asynccontextmanager
    async def lifespan(app):
        store.initialize()
        yield

    app = FastAPI(title="CodePilot", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "testserver"]
    )
    app.state.store = store
    app.state.settings = settings

    @app.get("/api/health")
    def health():
        return {"status": "ok", "schema_version": store.health(), "release": "foundation"}

    @app.get("/api/capabilities")
    def capabilities():
        return {
            "provider": settings.provider,
            "model": settings.model or None,
            "live_generation_verified": False,
            "runner_verified": False,
            "supported_targets": ["trusted Python 3.12 / pytest (planned)"],
            "milestone": "M0",
        }

    return app
