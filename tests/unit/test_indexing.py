import hashlib

import pytest
from codepilot.indexing import findings, index_snapshot, parse_source

SOURCE = b'''import math as maths
from helpers import work as action

def outer(value):
    """Documented function."""
    def inner(x):
        return x + 1
    if value:
        return inner(value)
    return obj.run()

class Service:
    @decorate
    async def run(self, value=1):
        return await action(value)
'''


def test_structures_and_approximate_calls():
    result = parse_source(SOURCE, "package/example.py", "a" * 40)
    by_name = {s["name"]: s for s in result["symbols"]}
    outer = by_name["package.example.outer"]
    assert outer["docstring"] == "Documented function."
    assert outer["metrics"]["branch_heuristic"] == 2
    assert outer["metrics"]["parameters"] == 1
    assert outer["metrics"]["nesting"] == 1
    assert by_name["package.example.outer.inner"]["parent"] == "package.example.outer"
    method = by_name["package.example.Service.run"]
    assert method["kind"] == "method" and method["async"]
    assert method["start_line"] == 13
    assert method["signature"].startswith("async def run")
    calls = {e["target_text"]: e for e in result["edges"] if e["kind"] == "call"}
    assert calls["inner"]["target"] == "package.example.outer.inner"
    assert calls["inner"]["resolution"] == "heuristic"
    assert calls["obj.run"]["resolution"] == "unresolved"
    assert calls["action"]["resolution"] == "unresolved"
    assert len([e for e in result["edges"] if e["kind"] == "import"]) == 2
    assert not result["parse_error"]


def test_malformed_source_is_visible():
    result = parse_source(b"def broken(:\n pass\n", "broken.py", "a" * 40)
    assert result["parse_error"]
    assert result["parser"]["binding"]


def test_findings_cite_source_ranges():
    index = {"files": [parse_source(SOURCE, "example.py", "a" * 40)]}
    result = findings(index, {"lines": 2})
    assert any(f["symbol"] == "example.outer" and f["start_line"] == 4 for f in result)
    assert all(f["value"] > 2 for f in result)


def test_snapshot_hash_guards_index(tmp_path):
    source = tmp_path / "sample.py"
    source.write_bytes(b"value = 1\n")
    manifest = {
        "base_sha": "a" * 40,
        "files": [{"path": "sample.py", "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}],
    }
    assert index_snapshot(tmp_path, manifest)["files"][0]["symbols"][0]["kind"] == "module"
    source.write_bytes(b"value = 2\n")
    with pytest.raises(ValueError, match="changed"):
        index_snapshot(tmp_path, manifest)
