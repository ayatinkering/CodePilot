# Enable draft pull requests

Publication is disabled for newly prepared fixtures. Enable it only for a repository
and branch you own or have permission to modify.

1. Authenticate the host with `gh auth login`.
2. Prepare a dedicated remote branch containing the controlled fixture. Keep it
   separate from the application's source branch.
3. Clone that branch into a local trusted target directory. A newly generated fixture
   has a different commit SHA, even if its files match, so use the actual remote commit.
4. Edit the matching entry in ignored `.codepilot/repositories.json`. Set `path` to
   the clone's absolute path, `publication_allowed` to `true`, `github_repo` to
   `owner/repository`, and `base_branch` to your dedicated branch. Preserve the entry's
   task, mode, evaluator and trusted settings. Set `CODEPILOT_GITHUB_REPO` in `.env`
   to the same repository and restart the application.
5. Start a new run. Review its diff and checks, then approve the exact patch and
   create a draft PR.

The remote base SHA must match the validated snapshot. If the base changed, start
and validate a new run. Changing a candidate after validation also prevents publication.
An ambiguous network failure is recorded as `publication_uncertain`; repeat approval
to reconcile the existing branch/PR instead of creating duplicate changes.

Authentication stays in the host's GitHub CLI configuration. It is never passed to
target containers. The application does not merge PRs or force-push branches.
