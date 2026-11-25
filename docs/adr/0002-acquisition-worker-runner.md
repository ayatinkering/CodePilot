# ADR 0002: Git-object snapshots and fail-closed worker

Date: 2026-11-25. Host orchestration implemented; container restrictions not live verified.

Read explicitly allowlisted local repositories at a resolved full commit SHA via
Git plumbing (`ls-tree`, `cat-file`). Reject symlink/traversal registration; skip
symlink/submodule modes, env/key files, generated directories and binaries.
Reading blobs avoids checkout hooks/filters, submodule downloads and working-tree
mutation. Alternative: git clone/worktree checkout is more familiar but needs
careful filter/hook controls. Current snapshots contain source without Git metadata;
publication will need separately controlled branch construction later.

Limitations: trusted local repositories only; no remote URL acquisition yet. Git
metadata/config itself is trusted operator input. Exclusions do not detect every
secret embedded in arbitrary source. Each blob is read separately (O(files) Git
processes); optimize only if measurements justify batching. Destination directories
are managed by the worker; arbitrary destinations are not accepted over an API.

Use SQLite BEGIN IMMEDIATE for claims and transition/event atomicity, plus a host
flock held for worker lifetime. Only the owner does startup recovery. Active runs
become interrupted; publishing becomes publication_uncertain. No automatic resume
or remote reconciliation is implemented. Cancellation is terminal and checked by
runner polling. A fresh retry command is still planned.

Runner commands are argument arrays, never model-authored shell. Container uses
non-root, no network, no capabilities, no-new-privileges, bounded tmpfs and resource
limits; source is copied into the container, no host mounts/socket/keys. Execution
requires an existing sha256 image ID and never downloads or installs dependencies.
Operator image build is separate and currently pins pytest but not transitive
image dependencies. No container boundary acceptance claimed until live tests pass.

Report classification distinguishes failures, collection/environment errors, zero
executed tests and missing runner. stdout reports are auxiliary evidence on trusted
targets, not tamper-proof proofs against malicious tests (which share the Python
process). Protected evaluator design is still required. If the daemon disappears,
cleanup may need operator reconciliation. This is not a public untrusted runner.
