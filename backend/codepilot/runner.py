"""Trusted host controller; target code runs only inside Docker."""

import json
import re
import subprocess
import time
import uuid
from pathlib import Path


def docker(*args, timeout=10):
    return subprocess.run(["docker", *args], capture_output=True, timeout=timeout, check=False)


def classify(report, exit_code):
    if not isinstance(report, dict) or not isinstance(report.get("tests"), list):
        return "environment_error"
    if report.get("collection_errors"):
        return "environment_error"
    if not report["tests"]:
        return "zero_tests"
    if any(t.get("outcome") == "failed" for t in report["tests"]):
        return "baseline_failed"
    if exit_code != 0:
        return "environment_error"
    if not any(t.get("outcome") == "passed" for t in report["tests"]):
        return "zero_tests"
    return "passed"


def run_tests(snapshot: Path, image: str, seconds=120, cancelled=lambda: False):
    if not 0 < seconds <= 120:
        raise ValueError("Test timeout must be in (0,120]")
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", image):
        return {"status": "environment_error", "reason": "runner_image_digest_required"}
    if cancelled():
        return {"status": "cancelled"}
    try:
        info = docker("image", "inspect", image, "--format", "{{.Id}}")
        if info.returncode or info.stdout.decode().strip() != image:
            return {"status": "environment_error", "reason": "runner_image_unavailable"}
    except (OSError, subprocess.TimeoutExpired):
        return {"status": "environment_error", "reason": "docker_unavailable"}
    name = "codepilot-" + uuid.uuid4().hex
    # Copy source through Docker's archive protocol: no writable host mounts, no secrets.
    args = [
        "create",
        "--name",
        name,
        "--log-driver=local",
        "--log-opt=max-size=1m",
        "--log-opt=max-file=1",
        "--network=none",
        "--read-only",
        "--cap-drop=ALL",
        "--security-opt=no-new-privileges",
        "--pids-limit=64",
        "--memory=512m",
        "--cpus=1",
        "--user=65534:65534",
        "--tmpfs=/tmp:rw,noexec,nosuid,size=64m",
        "--tmpfs=/work:rw,nosuid,size=64m",
        "--env=PYTHONDONTWRITEBYTECODE=1",
        image,
    ]
    started = time.monotonic()
    try:
        if docker(*args).returncode:
            return {"status": "environment_error", "reason": "container_create_failed"}
        if docker("cp", str(snapshot.resolve()) + "/.", name + ":/source").returncode:
            return {"status": "environment_error", "reason": "source_copy_failed"}
        # Bound Docker logs at the daemon and return only a capped tail.
        if docker("start", name).returncode:
            return {"status": "environment_error", "reason": "container_start_failed"}
        status = None
        while True:
            if cancelled():
                status = "cancelled"
                break
            if time.monotonic() - started >= seconds:
                status = "timeout"
                break
            state = docker("inspect", name, "--format", "{{json .State}}")
            if state.returncode:
                return {"status": "environment_error", "reason": "container_inspection_failed"}
            state = json.loads(state.stdout)
            if not state["Running"]:
                break
            time.sleep(0.1)
        if status:
            docker("kill", name)
            return {"status": status, "image": image}
        logs = docker("logs", "--tail=100", name).stdout[-65536:]
        report = None
        for line in logs.splitlines():
            if line.startswith(b"CODEPILOT_REPORT="):
                try:
                    report = json.loads(line[len(b"CODEPILOT_REPORT=") :])
                except ValueError:
                    pass
        return {
            "status": classify(report, state["ExitCode"]),
            "image": image,
            "exit_code": state["ExitCode"],
            "report": report,
            "duration_seconds": time.monotonic() - started,
        }
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return {"status": "environment_error", "reason": "docker_control_failed"}
    finally:
        try:
            docker("rm", "--force", name)
        except (OSError, subprocess.TimeoutExpired):
            pass  # Operator must reconcile orphan containers if the daemon is lost.
