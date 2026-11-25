import argparse
import json

from codepilot.config import Settings
from codepilot.storage import Store


def main():
    parser = argparse.ArgumentParser(description="CodePilot local control plane")
    parser.add_argument("command", choices=["health", "serve"])
    args = parser.parse_args()
    settings = Settings()
    if args.command == "serve":
        import uvicorn

        from codepilot.api import create_app

        uvicorn.run(create_app(settings), host="127.0.0.1", port=8000)
    else:
        store = Store(settings.data_dir / "codepilot.sqlite3")
        store.initialize()
        print(json.dumps({"status": "ok", "schema_version": store.health()}))
