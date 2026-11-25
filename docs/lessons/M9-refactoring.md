# M9: behavior-preserving refactoring

Repair intentionally changes incorrect behavior. Refactoring changes structure
while preserving behavior. The controlled `orders.py` fixture extracts a line-total
helper. Acceptance requires the original tests, a protected differential evaluator,
and a smaller `total_order` function. The evaluator compares the candidate with the
original calculation over negative, zero, positive and fractional prices and quantities.
This finite input set is useful evidence, not a mathematical equivalence proof.

Commit analysis compares the selected SHA with its first parent (or the empty tree
for the root commit), records changed paths, and lists symbols in those files. It is
conservative file-level impact analysis, not a precise semantic dependency graph.

The valid helper passes; the variant that changes negative-quantity behavior is
rejected. Unsupported refactoring targets abstain. Automatic smell selection,
arbitrary extract-method transformations and whole-program equivalence are outside
this basic version. A smaller function alone does not establish better design.

Exercise: add a new numerical edge case to the evaluator. Explain why fewer lines
can still conceal a regression and why generated tests alone are insufficient.
