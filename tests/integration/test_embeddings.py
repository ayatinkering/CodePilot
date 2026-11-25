import os
from pathlib import Path

import numpy as np
import pytest
from codepilot.indexing import parse_source
from codepilot.retrieval import REVISION, Embedder, build_index, search

DATA = Path(os.environ.get("CODEPILOT_DATA_DIR", ".codepilot"))
pytestmark = pytest.mark.skipif(
    not (DATA / "models" / REVISION / "model_optimized.onnx").exists(),
    reason="Pinned embedding model not downloaded",
)


def test_real_semantics_cache_and_deletion(tmp_path):
    embedder = Embedder(DATA)
    root = tmp_path / "root"
    root.mkdir()
    sources = {
        "invoice.py": 'def amount(values):\n    """Compute the sum of prices on an invoice."""\n    return sum(values)\n',
        "palette.py": 'def shade():\n    """Return the color blue."""\n    return "blue"\n',
    }
    for name, text in sources.items():
        (root / name).write_text(text)
    structure = {
        "base_sha": "a" * 40,
        "files": [parse_source(text.encode(), name, "a" * 40) for name, text in sources.items()],
    }
    index = build_index(root, structure, tmp_path / "index.json", tmp_path / "cache", embedder)
    assert np.array(index["vectors"]).shape == (2, 384)
    assert np.allclose(np.linalg.norm(index["vectors"], axis=1), 1, atol=1e-4)
    results = search(index, "calculate total bill", embedder, limit=1, expand=False)
    assert results[0]["path"] == "invoice.py"
    assert any(c["name"] == "semantic" for c in results[0]["channels"])
    again = build_index(root, structure, tmp_path / "again.json", tmp_path / "cache", embedder)
    assert again["cache_hits"] == 2
    structure["files"] = structure["files"][1:]
    deleted = build_index(root, structure, tmp_path / "deleted.json", tmp_path / "cache", embedder)
    assert all(r["path"] != "invoice.py" for r in search(deleted, "invoice total", embedder))
    deleted["model"] = "other-revision"
    with pytest.raises(ValueError, match="revision"):
        search(deleted, "total", embedder)
