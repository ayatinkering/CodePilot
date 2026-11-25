# M3: Finding relevant evidence

Objective: understand semantic search, lexical search and why neither proves a fix.
Prerequisites: M2 symbols and source ranges. An embedding is a learned numerical
representation, not a hash or reversible compression. Similar meanings can be
nearby in vector space. Our real CPU model is BAAI/bge-small-en-v1.5, exported as
Qdrant/bge-small-en-v1.5-onnx-Q at revision
c32e6154d1bb7a0e47c5e745fd895e7700f44385, 384 dimensions, normalized. The export card
labels Apache-2.0; upstream BGE/FastEmbed metadata labels MIT. No training occurs.

Source -> function-aware chunks -> learned vectors -> query vector -> cosine
ranking. For normalized vectors cosine is a dot product. Exact search costs O(Nd)
for N chunks and d=384. This is reasonable for the bounded small corpus; an ANN
index trades exact ranking for larger-scale speed and is not needed yet.

`retrieval.py` splits functions into 24-line/1800-character spans, keeps path,
symbol and line references, and stores per-run JSON. The model truncates at 512
tokens, so unusually dense chunks can lose tail context. Scores are not calibrated
correctness probabilities. Lexical token overlap complements semantic ranking;
reciprocal-rank fusion adds 1/(60+rank) from each channel. Bounded structural/test
neighbors expand context. A character budget bounds selected evidence.

Vectors cache by text/path/symbol plus exact model identity. Rebuilding a fresh
index naturally removes deleted symbols while reusing unchanged vectors. Changed
model identity is rejected at query time. Baseline and candidate indexes stay in
separate artifacts. This is content-based caching, not incremental parser editing.
The parent acquisition hash guards snapshot integrity. Cache files may contain
source-derived data and stay ignored/local.

Verification: actual ONNX inference retrieved invoice computation for “calculate
total bill”; 384-vector norms were checked, unchanged rebuild hit both cache
entries, deleting invoice removed it from search, and model mismatch raised an
error. Test: tests/integration/test_embeddings.py. Combined retrieval/patch checks:
9 passed in 0.85s on 2026-11-25. This is feasibility evidence, not a benchmark.

Beginner: Is RAG training? No, it supplies context at inference.
Intermediate: Why combine lexical and semantic? Exact identifiers and descriptive
queries have different strengths; fused ranks are a simple baseline.
Advanced: Can better retrieval worsen a result? Yes: irrelevant neighbors consume
context and similar code may mislead generation; compare controlled variants.
Exercise: delete a function and rerun the cache test. Teach-back: why aren't
similarity scores probabilities? What invalidates cached vectors? Unassessed.
