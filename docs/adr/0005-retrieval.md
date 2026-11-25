# ADR 0005: CPU ONNX embeddings and exact hybrid retrieval

2026-11-25. Choose FastEmbed with the pinned BGE-small ONNX export for a ~67MB
CPU model instead of a large PyTorch runtime or hosted embedding API. Real learned
embeddings are required even in offline-generation demos. Model preparation is an
explicit network download; inference uses a local path with no remote fallback.
Brute-force NumPy search and rank fusion are inspectable and sufficient for v1.
Chunk/cache metadata and limitations are in lessons/M3-retrieval.md.
Sources: https://huggingface.co/Qdrant/bge-small-en-v1.5-onnx-Q
https://qdrant.github.io/fastembed/Getting%20Started/
