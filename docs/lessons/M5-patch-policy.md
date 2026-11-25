# M5: A proposal becomes an inspectable candidate

Objective: distinguish model text from an authorized source change. A preimage is
the original file bytes; its SHA-256 hash binds an edit to exactly those bytes.
Input: path, expected hash, unique old text and replacement. Output: fresh candidate,
unified diff and diff digest. A digest is a fingerprint, not an approval by itself.

`patching.apply_edits` checks src/*.py scope, traversal/symlinks, duplicate files,
preimage hash, exact occurrence count, Python syntax and changed-line/file budgets
before copying anything. It writes a separate candidate, preserving baseline and
existing tests. `ast.parse` reads syntax without executing target code. Parsing is
not validation of behavior. The conventional diff is generated from actual results.

Trade-off: exact spans reject ambiguous/stale edits rather than guessing as a fuzzy
patch might. A rejected good intent can be retried with correct evidence. Costs
are proportional to copied source and edited file sizes, bounded by acquisition.
Tests demonstrate an accepted boundary edit and rejection of traversal, protected
tests, wrong hashes, missing/unchanged spans, malformed syntax and ambiguity.
Eight patch checks passed alongside the real retrieval check (9 combined).

Beginner: Why keep the baseline? To compare and preserve original user work.
Intermediate: Why hash plus exact text? Hash catches stale versions; uniqueness
prevents editing the wrong repeated occurrence.
Advanced: Does a parseable diff prove a repair? No; independent behavioral checks
must reject plausible wrong changes. These guards support repair and refactoring,
but don't prove equivalence or enforce every possible malicious Python behavior.
Exercise: add a second copy of the old span and predict the rejection. Teach-back:
why are tests protected? What happens after a failed candidate? Unassessed.
