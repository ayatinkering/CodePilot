# M7–M8: a reviewable local application

FastAPI accepts requests; a separate worker executes runs. SQLite records state and
ordered events. Server-sent events (SSE) notify the React dashboard of progress;
reloading restores a run from its URL. A periodic refresh handles missed events.
The dashboard exposes the exact diff, test outcomes, retrieved source, plan, history,
cancellation, retry, and downloadable evidence.

The API uses a local session cookie and checks mutation origins. It binds only to
loopback and accepts registered trusted fixtures, not arbitrary user-supplied paths.
This is a single-user boundary, not production multi-user authentication.

Issue ingestion reads a real GitHub issue using operator-owned `gh` authentication.
Issue text cannot enable publication. An operator must separately register the
remote repository and base branch. Approval includes the exact base SHA and patch
SHA256. Publication reconstructs the edit and compares every candidate file before
uploading. A deterministic branch and remote reconciliation prevent duplicate PRs.
Failures after an uncertain network response are labeled `publication_uncertain`.
A draft PR is a review artifact, never an automatic merge.

Exercise: change the approved digest and explain the resulting 409. Why must the
server enforce this even when the UI button is disabled? Why does a retry retain the
same base SHA? Why can a draft PR still contain an incorrect change?

Verification: API boundary tests, stale/candidate-tamper/idempotency tests, production
frontend build, and real issue→offline validation→draft PR. Browser automation was
unavailable because the desktop browser attachment required an app update; visual
layout and click-through verification remain outstanding.
