"""Immutable per-run hybrid index with reusable, model-versioned embedding cache."""

import hashlib
import json
import re
from pathlib import Path

import numpy as np

MODEL = "BAAI/bge-small-en-v1.5"
REPOSITORY = "Qdrant/bge-small-en-v1.5-onnx-Q"
REVISION = "c32e6154d1bb7a0e47c5e745fd895e7700f44385"
DIMENSION = 384


def prepare_model(data_dir: Path):
    from huggingface_hub import snapshot_download

    destination = data_dir / "models" / REVISION
    snapshot_download(
        REPOSITORY,
        revision=REVISION,
        local_dir=destination,
        token=False,
        allow_patterns=["*.json", "*.txt", "model_optimized.onnx", "README.md"],
    )
    return destination


class Embedder:
    def __init__(self, data_dir: Path):
        from fastembed import TextEmbedding

        path = data_dir / "models" / REVISION
        if not (path / "model_optimized.onnx").exists():
            raise ValueError("embedding_model_missing: run codepilot prepare-model")
        self.model = TextEmbedding(
            MODEL,
            specific_model_path=str(path),
            local_files_only=True,
            threads=2,
            providers=["CPUExecutionProvider"],
        )
        self.identity = f"{REPOSITORY}@{REVISION}:384:normalized"

    def embed(self, texts):
        vectors = np.array(list(self.model.embed(texts)), dtype=np.float32)
        return vectors / np.maximum(np.linalg.norm(vectors, axis=1, keepdims=True), 1e-12)


def chunks_from_index(root: Path, index: dict):
    chunks = []
    for file in index["files"]:
        lines = (root / file["path"]).read_text().splitlines(keepends=True)
        units = [s for s in file["symbols"] if s["kind"] in {"function", "method"}]
        if not units:
            units = [file["symbols"][0]]
        for symbol in units:
            start, end = symbol["start_line"] - 1, symbol["end_line"]
            # Bound spans by bytes/lines; model itself truncates at 512 tokens (recorded).
            for first in range(start, min(end, len(lines)), 24):
                last = min(first + 24, end, len(lines))
                source = "".join(lines[first:last])[:1800]
                identifier = f"{file['path']}:{first + 1}-{last}"
                chunks.append(
                    {
                        "id": identifier,
                        "path": file["path"],
                        "symbol": symbol["name"],
                        "start_line": first + 1,
                        "end_line": last,
                        "text": source,
                        "sha256": hashlib.sha256(source.encode()).hexdigest(),
                    }
                )
    return chunks


def build_index(root: Path, structural: dict, output: Path, cache: Path, embedder):
    chunks = chunks_from_index(root, structural)
    cache.mkdir(parents=True, exist_ok=True)
    vectors, hits = [], 0
    for chunk in chunks:
        text = f"{chunk['path']} {chunk['symbol']}\n{chunk['text']}"
        key = hashlib.sha256((embedder.identity + text).encode()).hexdigest()
        target = cache / (key + ".npy")
        if target.exists():
            vector = np.load(target, allow_pickle=False)
            hits += 1
        else:
            vector = embedder.embed([text])[0]
            np.save(target, vector, allow_pickle=False)
        if vector.shape != (DIMENSION,) or not np.isfinite(vector).all():
            raise ValueError("embedding_dimension_or_values_invalid")
        vectors.append(vector.tolist())
    result = {
        "base_sha": structural["base_sha"],
        "model": embedder.identity,
        "chunks": chunks,
        "vectors": vectors,
        "cache_hits": hits,
        "parser": [f["parser"] for f in structural["files"]],
        "edges": [e for f in structural["files"] for e in f["edges"]],
    }
    output.write_text(json.dumps(result))
    return result


def search(index, query: str, embedder, limit=6, expand=True, variant="hybrid"):
    if index["model"] != embedder.identity:
        raise ValueError("embedding_revision_mismatch")
    if not index["chunks"]:
        return []
    tokens = set(re.findall(r"\w+", query.lower()))
    lexical = [
        len(tokens & set(re.findall(r"\w+", (c["symbol"] + " " + c["text"]).lower())))
        for c in index["chunks"]
    ]
    semantic = np.array(index["vectors"]) @ embedder.embed([query])[0]
    ranks = {}
    for channel, values in [("lexical", lexical), ("semantic", semantic)]:
        for rank, idx in enumerate(sorted(range(len(values)), key=lambda i: -values[i]), 1):
            if channel == "lexical" and values[idx] == 0:
                continue
            row = ranks.setdefault(idx, {"score": 0.0, "channels": []})
            row["score"] += 1 / (60 + rank)
            row["channels"].append({"name": channel, "rank": rank, "value": float(values[idx])})
    selected = sorted(ranks, key=lambda i: -ranks[i]["score"])[:limit]
    if variant == "minimal":
        selected = list(range(min(2, len(index["chunks"]))))
    if expand and variant != "minimal":
        names = {index["chunks"][i]["symbol"] for i in selected}
        neighbors = {e["target"] for e in index["edges"] if e["source"] in names and e["target"]}
        for i, chunk in enumerate(index["chunks"]):
            if i not in selected and (
                chunk["symbol"] in neighbors or chunk["path"].startswith("tests/")
            ):
                selected.append(i)
                ranks.setdefault(i, {"score": 0.0, "channels": []})["channels"].append(
                    {"name": "structural_or_tests"}
                )
                if len(selected) >= limit + 2:
                    break
    result, used = [], 0
    for i in selected:
        chunk = index["chunks"][i]
        if used + len(chunk["text"]) > 10000:
            break
        used += len(chunk["text"])
        result.append({**chunk, **ranks.get(i, {"score": 0.0, "channels": [{"name": "minimal"}]})})
    return result
