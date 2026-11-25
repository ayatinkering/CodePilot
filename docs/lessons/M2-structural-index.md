# M2: Reading program structure without executing it

## Objectives and prerequisites
Build on immutable snapshots. Understand tokens (small lexical pieces), parsing
(recognizing syntax), CST (concrete syntax tree), AST (abstract syntax tree), scope
(where a name is visible) and static analysis (examining code without running it).
A call graph connects potential callers/callees; a control-flow graph connects
possible execution steps; data-flow analysis tracks where values may travel.
Our index is not the latter two and is not a complete call graph.

## Small example and analogy
For `def outer(x): return inner(x)`, the parser recognizes a function definition,
parameter, return statement and call. We save source coordinates and the text
`inner`. If a local symbol matches we label it heuristic. For `obj.run()` we leave
the target unresolved. Like a map of rooms, syntax shows structure but not who will
walk through it. The analogy fails because Python can rebind names dynamically.

Input bytes -> Tree-sitter CST -> normalized symbols/calls -> JSON evidence.
A malformed `def broken(:` is marked parse_error. It is not silently accepted as
valid code, and a later generator must treat that evidence cautiously.

## Actual code walkthrough
`indexing.parse_source` constructs the parser, walks named nodes and records
module/class/function/method metadata. A method is directly inside a class; a
nested function has its function parent. Decorated symbols include the decorator
in their range; signatures retain async/default/annotation text. `docstring` uses
literal_eval on a string literal only; target code is never imported or executed.

Calls save enclosing scope, expression text and line. A local identifier search
walks outward through qualified scopes. Even a unique match is only heuristic:
monkey-patching, local assignment or Python's class-scope rules may change binding.
Raw import statements preserve alias syntax but aliases are not resolved yet.
Soundness means not missing possible behavior; completeness has different formal
uses, but our practical claim is simple: we do not enumerate all runtime targets.

`metrics` skips nested definitions while measuring a function. Branch heuristic
counts configured if/loop/exception/case/conditional/boolean nodes plus one.
Nesting counts selected block ancestors. Parameter count excludes separator nodes.
`findings` compares metrics with configurable thresholds and cites exact ranges.
A large number is a review signal, not a verdict that code is bad. Extracting helpers
can reduce line count while worsening coupling or hiding behavior.

`index_snapshot` checks source hashes against the acquisition manifest. A changed
file raises an error. JSON output keeps the immutable base SHA and parser versions
so evidence can be audited. Traversal is roughly O(nodes), but metric ancestor
walks add depth-dependent cost; this is bounded small-repository analysis.

## Alternatives and research connection
Python ast is built in and good for valid Python. Tree-sitter supports partial
syntax on malformed source; regex loses nesting and grammar information. See ADR
0003 for the actual trade-off. Structural evidence can help retrieve relevant
functions for repair and locate maintainability candidates for refactoring. It
alone proves neither behavior nor refactoring safety. No DPy reproduction claimed.

## Verification and limitations
`test_indexing.py` covers decorated async methods, nested functions, signatures,
docstrings, raw alias imports, unresolved dynamic calls, malformed files, range
findings and stale hash rejection. Exact results are in M2-verification.md.
The fixture `inner(value)` gets a heuristic target; `obj.run()` and imported
`action(value)` remain unresolved. This is an intentional limitation, not an error
hidden by a pretty graph. Cross-file import resolution and incremental caching
remain planned. Tests do not show retrieval relevance or live model correctness.

## Interview questions
Beginner: Is Tree-sitter an LLM? No, it is a syntax parser driven by a grammar.
Intermediate: CST versus AST? Tree-sitter retains concrete source structure; our
symbol records are a selective abstraction derived from it, not the full CST.
Advanced: Why not call this a complete call graph? Runtime dispatch, rebinding,
imports and aliasing can change targets. We expose unresolved/heuristic status.

## Exercise and teach-back (unassessed)
Add a nested `if` to the fixture and predict nesting/branch changes, then run
`uv run --locked pytest tests/unit/test_indexing.py -q`. Add a method call through
an unknown object and inspect resolution. Why can syntax not tell its type?
Why does a shorter function not necessarily mean better code? What should happen
if the snapshot changes after indexing?

<details><summary>Guidance</summary>
A nested if raises the branch count and may raise max nesting. Unknown object
calls remain unresolved. A shorter function may hide complexity elsewhere. Hash
mismatches must invalidate evidence rather than silently mixing snapshots.
</details>
