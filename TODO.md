# helper-scripts: outstanding TODOs

## Coverity Scan: HTTP 401 on tarball download

Pre-existing condition (every Coverity run since 2026-05-06 has
failed); not introduced by the dev-meta-files reusable migration.

### What's already fixed (master)

- Workflow uses the org-wide reusable in
  `org-ai-assisted/developer-meta-files/.github/workflows/coverity.yml`.
- Project name corrected to `Kicksecure-helper-scripts` (commit
  `f761e8b`) - matches the project page at
  https://scan.coverity.com/projects/Kicksecure-helper-scripts .
- Variable / URL / form-field audit clean: secret names
  (`COVERITY_SCAN_TOKEN`, `COVERITY_SCAN_EMAIL`), env mapping
  (`COVERITY_TOKEN` / `COVERITY_EMAIL` / `COVERITY_PROJECT`),
  endpoints (`/download/linux64`, `/builds?project=...`), and
  form fields (`token` / `project` / `email` / `file` / `version`
  / `description`) all match Coverity Scan's documented API and
  the pre-refactor inline workflow.

### What's blocking

`scan.coverity.com` returns HTTP 401 on the `/download/linux64`
endpoint when the workflow runs. The check-secrets step passes
(both secrets are set and non-empty), so the secret VALUES are
the problem rather than missing-ness. The `COVERITY_SCAN_TOKEN`
repo secret was last updated on 2026-05-06 (per the secrets API
metadata); subsequent project-token rotations on
scan.coverity.com would not have been mirrored back to the repo.

### One-time fix required

1. Sign in to https://scan.coverity.com/projects/Kicksecure-helper-scripts
   (needs maintainer access on the Coverity project).
2. Project Settings -> Project Token -> copy current value.
3. On GitHub: Settings -> Secrets and variables -> Actions ->
   Repository secrets -> Update `COVERITY_SCAN_TOKEN` with the
   exact token.
4. Re-trigger via Actions -> Coverity -> "Run workflow" (manual
   workflow_dispatch). Expected outcome: download succeeds,
   cov-build runs, submission lands at
   https://scan.coverity.com/projects/Kicksecure-helper-scripts .

`COVERITY_SCAN_EMAIL` may already be correct (the workflow runs
far enough to dispatch the curl); refresh it too if the email on
the Coverity project changed since 2026-05-06.

The same fix is pending in parallel on `org-ai-assisted/kloak`
(project `Whonix-kloak`) and `org-ai-assisted/security-misc`
(project `Kicksecure-security-misc`).
