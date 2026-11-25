# ADR 0006: Exact source edits, immutable baseline

Use structured preimage edits rather than fuzzy unified diff application. Limit MVP
to existing src/*.py production files and three files/50 changed lines. Original
tests, manifests and CI cannot be edited. Generated tests are separate auxiliary
artifacts. Validate all edits before writing a fresh candidate. Generate a normal
unified diff after application and bind later publication to its digest.
Unsupported tasks abstain; no user worktree mutation or automatic merging.
