"""Opt-in real boundary checks; fixtures execute ONLY in Docker, never on host."""

import os
import subprocess
import time

import pytest
from codepilot.runner import run_tests

IMAGE = os.environ.get("CODEPILOT_TEST_RUNNER_IMAGE", "")
pytestmark = pytest.mark.skipif(
    not IMAGE, reason="Set CODEPILOT_TEST_RUNNER_IMAGE to opt into Docker checks"
)


def fixture_source(tmp_path, text):
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_target.py").write_text(text)
    return tmp_path


@pytest.mark.parametrize(
    "text,expected",
    [
        ("def test_ok(): assert 1 + 1 == 2\n", "passed"),
        ("def test_failure(): assert False\n", "baseline_failed"),
        ("import dependency_that_does_not_exist\n", "environment_error"),
        ("# no tests\n", "zero_tests"),
    ],
)
def test_real_classification(tmp_path, text, expected):
    result = run_tests(fixture_source(tmp_path, text), IMAGE, 30)
    assert result["status"] == expected, result


def test_container_boundaries(tmp_path, monkeypatch):
    monkeypatch.setenv("CODEPILOT_TEST_HOST_SECRET", "synthetic-sentinel")
    source = fixture_source(
        tmp_path,
        """
import os
import socket
from pathlib import Path
import pytest

def test_boundaries():
    assert os.getuid() == 65534
    assert 'CODEPILOT_TEST_HOST_SECRET' not in os.environ
    assert 'GEMINI_API_KEY' not in os.environ
    assert 'GITHUB_TOKEN' not in os.environ
    assert not Path('/var/run/docker.sock').exists()
    status = Path('/proc/self/status').read_text()
    fields = dict(line.split(':', 1) for line in status.splitlines() if ':' in line)
    assert int(fields['CapEff'].strip(), 16) == 0
    assert fields['NoNewPrivs'].strip() == '1'
    assert fields['Seccomp'].strip() == '2'
    with pytest.raises(OSError):
        Path('/source/forbidden').write_text('no')
    with pytest.raises(OSError):
        Path('/etc/forbidden').write_text('no')
    with socket.socket() as client:
        client.settimeout(0.5)
        with pytest.raises(OSError):
            client.connect(('1.1.1.1', 53))
    Path('/work/allowed').write_text('yes')
""",
    )
    result = run_tests(source, IMAGE, 30)
    assert result["status"] == "passed", result
    assert not (source / "forbidden").exists()


@pytest.mark.parametrize("cancel", [False, True])
def test_timeout_cancel_and_cleanup(tmp_path, cancel):
    before_containers = subprocess.check_output(
        ["docker", "ps", "-aq", "--filter", "name=codepilot-"]
    )
    before_volumes = subprocess.check_output(
        ["docker", "volume", "ls", "-q", "--filter", "name=codepilot-"]
    )
    source = fixture_source(tmp_path, "def test_loop():\n    while True: pass\n")
    start = time.monotonic()
    result = run_tests(
        source,
        IMAGE,
        30 if cancel else 4,
        cancelled=lambda: cancel and time.monotonic() - start > 4,
    )
    assert result["status"] == ("cancelled" if cancel else "timeout"), result
    assert (
        subprocess.check_output(["docker", "ps", "-aq", "--filter", "name=codepilot-"])
        == before_containers
    )
    assert (
        subprocess.check_output(["docker", "volume", "ls", "-q", "--filter", "name=codepilot-"])
        == before_volumes
    )
