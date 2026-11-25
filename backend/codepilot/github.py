"""Opt-in GitHub publication for operator-registered demo branches only."""

import fcntl
import json
import subprocess

from codepilot.config import Budgets
from codepilot.demo import registry
from codepilot.patching import Proposal, apply_edits


class GitHubError(RuntimeError):
    pass


def github(path, method="GET", payload=None):
    command = ["gh", "api", "--method", method, path]
    if payload is not None:
        command += ["--input", "-"]
    try:
        reply = subprocess.run(
            command,
            input=json.dumps(payload) if payload is not None else None,
            text=True,
            capture_output=True,
            timeout=45,
            check=True,
        )
        return json.loads(reply.stdout) if reply.stdout.strip() else {}
    except (subprocess.SubprocessError, OSError, ValueError) as exc:
        raise GitHubError(
            "GitHub request failed; check gh authentication and connectivity"
        ) from exc


def import_issue(settings, number):
    issue = github(f"repos/{settings.github_repo}/issues/{number}")
    if "pull_request" in issue:
        raise ValueError("Choose an issue, not a pull request")
    return {
        "number": number,
        "url": issue["html_url"],
        "task": (issue["title"] + "\n\n" + (issue.get("body") or ""))[:10000],
    }


def verify_candidate(directory, result, budgets):
    """Recreate the approved edit, then compare every candidate byte before upload."""
    import tempfile
    from pathlib import Path

    attempt = result["attempts"][result["approved_candidate"]]
    candidate = directory / f"candidate-{attempt['attempt']}"

    def files(root):
        entries = {}
        for path in root.rglob("*"):
            if path.is_symlink():
                raise ValueError("Symlink in approved candidate")
            if path.is_file():
                entries[path.relative_to(root).as_posix()] = path.read_bytes()
        return entries

    with tempfile.TemporaryDirectory(dir=directory) as tmp:
        reconstructed = Path(tmp) / "candidate"
        patch = apply_edits(
            directory / "baseline",
            reconstructed,
            Proposal.model_validate(attempt["proposal"]),
            budgets,
        )
        if patch["patch_digest"] != result["patch_digest"] or files(candidate) != files(
            reconstructed
        ):
            raise ValueError("Candidate changed after validation; run again")
    return patch, candidate


def publish(jobs, settings, run_id, expected_base, expected_digest):
    directory = settings.data_dir / "runs" / run_id
    with (settings.data_dir / "publication.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        run = jobs.get(run_id)
        result = json.loads((directory / "result.json").read_text())
        if expected_base != run["base_sha"] or expected_digest != result.get("patch_digest"):
            raise ValueError("Approval does not match the validated base and patch")
        if run["state"] == "published":
            return json.loads((directory / "publication.json").read_text())
        if run["state"] not in {"ready_for_review", "publication_uncertain"}:
            raise ValueError("Run is not ready for publication")
        task = json.loads(run["task_json"])
        entry = registry(settings.data_dir).get(task["repository_id"], {})
        if not entry.get("publication_allowed") or entry.get("github_repo") != settings.github_repo:
            raise ValueError("Operator has not enabled publication for this fixture")
        patch, candidate = verify_candidate(
            directory, result, Budgets.model_validate_json(run["budgets_json"])
        )
        repo = settings.github_repo
        prefix = f"repos/{repo}"
        base_branch = entry["base_branch"]
        base = github(f"{prefix}/git/ref/heads/{base_branch}")["object"]["sha"]
        if base != expected_base:
            raise ValueError("Remote base changed; create and validate a new run")
        branch = "codepilot/run-" + run_id
        marker = f"CodePilot run {run_id}; patch {expected_digest}"
        jobs.transition(run_id, "publishing")
        try:
            # Reconcile both branch and PR after ambiguous network failures; never force push.
            refs = github(f"{prefix}/git/matching-refs/heads/{branch}")
            exact = [r for r in refs if r["ref"] == "refs/heads/" + branch]
            if exact:
                commit = github(f"{prefix}/git/commits/{exact[0]['object']['sha']}")
                if commit["message"] != marker or [p["sha"] for p in commit["parents"]] != [base]:
                    raise ValueError("Existing publication branch does not match this run")
            else:
                base_commit = github(f"{prefix}/git/commits/{base}")
                tree = github(
                    f"{prefix}/git/trees",
                    "POST",
                    {
                        "base_tree": base_commit["tree"]["sha"],
                        "tree": [
                            {
                                "path": p,
                                "mode": "100644",
                                "type": "blob",
                                "content": (candidate / p).read_text(),
                            }
                            for p in patch["files"]
                        ],
                    },
                )
                commit = github(
                    f"{prefix}/git/commits",
                    "POST",
                    {"message": marker, "tree": tree["sha"], "parents": [base]},
                )
                github(
                    f"{prefix}/git/refs",
                    "POST",
                    {"ref": "refs/heads/" + branch, "sha": commit["sha"]},
                )
            prs = github(
                f"{prefix}/pulls?state=all&head={repo.split('/')[0]}:{branch}&base={base_branch}"
            )
            if prs:
                pr = prs[0]
            else:
                attempt = result["attempts"][result["approved_candidate"]]
                provenance = json.loads(run["provider_json"])
                generation = (
                    f"Live Gemini-generated proposal ({provenance.get('model')})."
                    if provenance["provider"] == "gemini"
                    else "Offline scripted proposal; not live AI."
                )
                body = (
                    f"Controlled CodePilot demonstration. **{generation}**\n\n"
                    f"Base: `{base}`\nPatch: `{expected_digest}`\n\n"
                    f"Existing tests: {attempt['existing_tests']['status']}. "
                    f"Protected evaluator: {attempt['evaluator_tests']['status']}.\n\n"
                    "Tests ran in restricted Docker containers. Evaluator evidence covers only the "
                    "curated fixture, not arbitrary projects. No automatic merge.\n\n"
                    f"Source issue: {task.get('issue_url', 'local demonstration task')}\n\n{marker}"
                )
                pr = github(
                    f"{prefix}/pulls",
                    "POST",
                    {
                        "title": f"[CodePilot demo] {task['mode']}: {task['repository_id']}",
                        "head": branch,
                        "base": base_branch,
                        "body": body,
                        "draft": True,
                    },
                )
            publication = {
                "url": pr["html_url"],
                "number": pr["number"],
                "branch": branch,
                "base_sha": base,
                "patch_digest": expected_digest,
            }
            (directory / "publication.json").write_text(json.dumps(publication, indent=2))
            jobs.transition(run_id, "published")
            return publication
        except Exception:
            jobs.transition(
                run_id, "publication_uncertain", "Check remote state before retrying publication"
            )
            raise
