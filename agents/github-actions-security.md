# GitHub Actions security - required patterns

When editing `.github/workflows/*.yml`, every workflow MUST:

1. **`permissions: contents: read` at the workflow top level.**
   Override per-job (e.g. `security-events: write` for codeql) only when
   strictly needed.

2. **`persist-credentials: false` on every `actions/checkout`.**
   The default leaves `GITHUB_TOKEN` in `.git/config` for any
   subsequent step to harvest. None of our workflows push, so always
   drop credentials post-checkout.

3. **Fork-PR guard on jobs that touch secrets or trigger builds:**
   ```
   if: github.event.pull_request.head.repo.full_name == github.repository
       || github.event_name != 'pull_request'
   ```

4. **Never interpolate `${{ github.event.* }}` (or `${{ inputs.* }}`,
   `${{ github.head_ref }}`, etc.) directly into `run:` shell.**
   Route through `env:` instead:
   ```
   env:
     TITLE: ${{ github.event.issue.title }}
   run: |
     echo "$TITLE"   # safe; not subject to expression-engine substitution
   ```
   Direct interpolation into `run:` is the cycode/Trojan-Source script-
   injection attack class.

5. **Pin `uses:` actions and Docker `image:` to commit SHA / digest.**
   Tags are mutable. Dependabot (`.github/dependabot.yml`) will bump SHAs
   automatically; do not change tags by hand to "latest" / "v6".

6. **Hard timeout on every job** (`timeout-minutes:`).

7. **Inline shell only for steps that must run before checkout** (e.g.
   `apt-get install git ca-certificates` before `actions/checkout`).
   Everything else should call a script under `ci/*.sh` so the bash
   is shellcheck/`bash -n` covered by the lint workflow and runnable
   locally.

If ANY of the above is missing in a workflow you edited, restore it
before committing.

## Why no actionlint

[`rhysd/actionlint`](https://github.com/rhysd/actionlint) catches
workflow-specific bugs that `python3 -c 'yaml.safe_load(...)'` and
shellcheck (on the file tree) don't see - script injection from
`${{ github.event.* }}` into `run:` blocks, mistyped action refs,
shellcheck-of-embedded-shell. It would be useful in principle.

We don't run it because:

- It is not packaged in Debian (`packages.debian.org` has no
  `actionlint` binary). Pulling it from upstream means trusting a
  single-maintainer GitHub release for a tool that runs in CI - same
  trust footprint as the workflow steps it's auditing.
- It is not a "GitHub-verified" Marketplace action; `actionlint`
  itself is a CLI, and the third-party `rhysd/actionlint-action`
  wrapper has the same single-maintainer concern.
- The script-injection class it would catch is already enforced by
  rule 4 above (`env:`-route every external string), and the
  embedded-shell-shellcheck class is mitigated by rule 7 (inline
  shell only when unavoidable).

If `actionlint` ever ships in Debian, we add it back via apt.

---

## Pinned-action provenance

Every `uses: <action>@<sha>` line in our workflows MUST cite a verifiable
source for the SHA. Dependabot bumps will replace this list automatically;
when bumping by hand, update this table at the same time.

The format is:

> **`<action>@<sha>  # v<tag>`**
>
> - Source: `<URL of the GitHub release page>`
> - Verbatim quote from the source: `"<commit hash shown there>"`
> - Verified: `<YYYY-MM-DD>` by `<who/how>`

### Currently pinned

**`actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd  # v6.0.2`**
- Source: https://github.com/actions/checkout/releases/tag/v6.0.2
- Verbatim quote: `"de0fac2e4500dabe0009e67214ff5f5447ce83dd"` (under "Assets" / "This commit was created on GitHub.com" indicator on the tag page).
- Verified: 2026-04 by direct fetch of the release / tag page.

**`actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405  # v6.2.0`**
- Source: https://github.com/actions/setup-python/releases/tag/v6.2.0
- Verbatim quote: `"a309ff8b426b58ec0e2a45f0f869d46889d02405"`.
- Verified: 2026-04.

**`actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a  # v7.0.1`**
- Source: https://github.com/actions/upload-artifact/releases/tag/v7.0.1
- Verbatim quote: `"043fb46d1a93c77aae656e7c1c64a875d1fc6a0a"`.
- Verified: 2026-04.

**`github/codeql-action/{init,analyze,upload-sarif}@95e58e9a2cdfd71adc6e0353d5c52f41a045d225  # v4.35.2`**
- Source: https://github.com/github/codeql-action/releases/tag/v4.35.2
- Verbatim quote: `"95e58e9a2cdfd71adc6e0353d5c52f41a045d225"`.
- Verified: 2026-04.
- Note: codeql-action is a monorepo - all three sub-actions share the same SHA.

**`ossf/scorecard-action@4eaacf0543bb3f2c246792bd56e8cdeffafb205a  # v2.4.3`**
- Source: https://github.com/ossf/scorecard-action/releases/tag/v2.4.3
- Verbatim quote: `"4eaacf0543bb3f2c246792bd56e8cdeffafb205a"`.
- Verified: 2026-04.

**`google/clusterfuzzlite/actions/{build_fuzzers,run_fuzzers}@884713a6c30a92e5e8544c39945cd7cb630abcd1  # v1`**
- Source: https://github.com/google/clusterfuzzlite/tree/v1 (HEAD of the v1 branch; ClusterFuzzLite does not cut numbered releases).
- Verbatim quote: `"884713a6c30a92e5e8544c39945cd7cb630abcd1"` (HEAD of v1 at time of pin).
- Verified: 2026-04.
- Note: there is no immutable release tag; we re-verify HEAD of v1 manually before each bump.

### Container image digests (Docker Hub)

Workflow `image:` lines must also be pinned to a content digest. Tags
are mutable.

**`debian:trixie@sha256:35b8ff74ead4880f22090b617372daff0ccae742eb5674455d542bef71ef1999`** (2026-04-27)
- Source: Docker Hub registry API. Re-pin with:
  ```
  curl -sS -I \
    -H 'Accept: application/vnd.oci.image.index.v1+json, application/vnd.docker.distribution.manifest.list.v2+json' \
    -H "Authorization: Bearer $(curl -sS 'https://auth.docker.io/token?service=registry.docker.io&scope=repository:library/debian:pull' | python3 -c 'import json,sys; print(json.load(sys.stdin)["token"])')" \
    'https://index.docker.io/v2/library/debian/manifests/trixie' \
    | grep -i 'docker-content-digest:'
  ```
- Multi-arch index digest. Used by both `lint.yml` and `dry-run.yml`;
  bump both call sites in lockstep.

Dependabot does NOT auto-bump container digests in workflow `image:`,
so this needs manual re-pinning when porting to a new Debian release.

### Procedure when adding or bumping a pin

1. Open the action's release page on github.com (`/<owner>/<action>/releases/tag/<version>`).
2. Copy the exact SHA shown there (40 hex chars).
3. Replace the `@<sha>  # v<tag>` line in the workflow.
4. Add (or update) a row in the "Currently pinned" list above with the same source URL.
5. Commit the workflow change and the doc update **in the same commit** so review can verify both at once.
