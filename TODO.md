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

> Update 2026-05-08: token refresh for all three projects will
> happen in the upstream non-fork orgs (Kicksecure / Whonix), not
> here. Until then the workflow keeps failing at the curl 401 on
> all three forks; the failure is loud and obvious so it is not
> silently masking other bugs.
>
> Note about `Whonix-kloak` specifically: the upstream
> `Whonix/kloak` CI submits successfully (last analyzed ~6h before
> this writeup). Once `org-ai-assisted/kloak`'s token is also
> valid, both fork and upstream submissions will land on the same
> dashboard with latest-wins semantics. Acceptable for short-
> lived fork branches; if it becomes an audit problem, register
> a separate `org-ai-assisted-kloak` project on
> scan.coverity.com or disable the fork's Coverity workflow.

## Coverity dashboard membership: add `assisted-by-ai`

To audit existing defects and verify successful submissions on
scan.coverity.com, the bot account `assisted-by-ai` (and any
other AI-assisted-flow operator account) needs to be added as a
project member on each Coverity project.

Owner action (Patrick / `adrelanos`, who created the projects):

1. https://scan.coverity.com/projects/Kicksecure-helper-scripts
   -> Project Settings -> Members -> Add `assisted-by-ai`.
2. Same for https://scan.coverity.com/projects/Whonix-kloak .
3. Same for https://scan.coverity.com/projects/Kicksecure-security-misc .

Without membership, the public project pages only expose
defect-count summaries; the per-defect detail view (line, rule,
trace) and the Project Token rotation UI both require sign-in
with a member account. The token-rotation access is what
unblocks the "refresh `COVERITY_SCAN_TOKEN`" step above for any
operator who is not the original owner.
