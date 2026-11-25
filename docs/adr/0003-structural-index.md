# ADR 0003: Tree-sitter extraction, conservative call references

2026-11-25. Use tree-sitter 0.27.0 with tree-sitter-python 0.25.0, resolved and
installed together; exact versions also in uv.lock and per-file index metadata.
Both upstream projects use MIT licensing. No model downloaded in this milestone.
Official binding reference: https://github.com/tree-sitter/py-tree-sitter

Tree-sitter produces a concrete syntax tree including source structure; CodePilot
normalizes selected nodes into AST-like symbol records. Python ast is a reasonable
simpler alternative for valid Python, but Tree-sitter's error-tolerant syntax tree
preserves useful partial evidence on malformed files. Regex is insufficient for
nested language structures. We do not implement a type checker, CFG or data-flow
engine, nor exploit incremental Tree-sitter tree edits in this milestone.

Index module/class/function/method, parent scope, full signature, docstring,
decorator-inclusive range, async status, file hash, base SHA and parse error.
Capture raw import text (including aliases) and call expressions. Name/scope
matches are heuristic, not sound resolved_local edges: Python rebinding and runtime
dispatch can invalidate them. Import alias resolution and cross-file graph linking
remain unfinished; unresolved references are retained for inspection.

Maintainability signals: physical function lines excluding decorators, parameter
nodes excluding positional/keyword separators, max nesting across selected block
nodes, and 1 + count of selected branch nodes. Skip nested definitions for parent
metrics. This is a transparent branch heuristic, not a formal complexity proof.
Threshold findings cite source ranges and are advisory. No refactoring is applied.
Snapshots are hash-checked before parsing; changed source cannot silently reuse
old evidence. Incremental cache and semantic retrieval remain later work.
