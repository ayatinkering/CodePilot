"""Operator-only preparation of versioned, trusted demonstration repositories."""

import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TASKS = {
    "boundary": "Customers aged 18 and above qualify for the discount. Fix the boundary condition without changing other behavior.",
    "refactor": "Extract the positive-quantity line calculation from total_order into a helper. Preserve behavior for all prices and quantities.",
    "baseline_failed": "Repair the discount boundary.",
    "missing_dependency": "Repair the discount boundary.",
    "zero_tests": "Repair the discount boundary.",
}


def registry(data_dir: Path):
    path = data_dir / "repositories.json"
    return json.loads(path.read_text()) if path.exists() else {}


def prepare_demo(data_dir: Path):
    entries = registry(data_dir)
    for name, task in TASKS.items():
        target = (data_dir / "targets" / name).resolve()
        if not target.exists():
            template = "refactor" if name == "refactor" else "boundary"
            shutil.copytree(ROOT / "fixtures" / "targets" / template, target)
            if name == "baseline_failed":
                (target / "tests/test_existing_failure.py").write_text(
                    "def test_existing_failure():\n    assert False\n"
                )
            elif name == "missing_dependency":
                (target / "tests/test_dependency.py").write_text(
                    "import codepilot_dependency_not_installed\n"
                )
            elif name == "zero_tests":
                shutil.rmtree(target / "tests")
                (target / "tests").mkdir()
                (target / "tests/.gitkeep").write_text("")
            commands = [
                ["init", "-b", "codex/demo-fixture"],
                ["config", "user.name", "CodePilot demo"],
                ["config", "user.email", "codepilot-demo@example.invalid"],
                ["add", "src", "tests"],
                ["commit", "-m", "Add AI-assisted controlled CodePilot demo fixture"],
            ]
            for command in commands:
                subprocess.run(
                    ["git", "-C", str(target), *command], check=True, capture_output=True
                )
        previous = entries.get(name, {})
        entries[name] = {
            "id": name,
            "path": str(target),
            "task": task,
            "mode": "refactor" if name == "refactor" else "repair",
            "evaluator": name if name in {"boundary", "refactor"} else None,
            "trusted": True,
            "publication_allowed": previous.get("publication_allowed", False),
            **{k: previous[k] for k in ("github_repo", "base_branch") if k in previous},
        }
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "repositories.json").write_text(json.dumps(entries, indent=2))
    return entries
