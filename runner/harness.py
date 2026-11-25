"""Trusted image harness. Only executed in the restricted target container."""

import json
import os
import shutil
import sys

import pytest


class Report:
    def __init__(self):
        self.outcomes = {}
        self.collection_errors = []

    def pytest_collectreport(self, report):
        if report.failed:
            self.collection_errors.append(str(report.nodeid)[:500])

    def pytest_runtest_logreport(self, report):
        # A teardown/setup failure must not be overwritten by a passing call.
        old = self.outcomes.get(report.nodeid)
        if report.failed or old != "failed" and report.when == "call":
            self.outcomes[report.nodeid] = report.outcome


shutil.copytree("/source", "/work/project")
os.chdir("/work/project")
sys.path.insert(0, "/work/project")
os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
report = Report()
code = pytest.main(
    ["tests", "-q", "-c", "/dev/null", "--override-ini=addopts=", "-p", "no:cacheprovider"],
    plugins=[report],
)
print(
    "CODEPILOT_REPORT="
    + json.dumps(
        {
            "tests": [{"id": k, "outcome": v} for k, v in list(report.outcomes.items())[:1000]],
            "collection_errors": report.collection_errors[:100],
        }
    ),
    flush=True,
)
raise SystemExit(code)
