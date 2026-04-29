## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## Authored by Claude (Anthropic).

# GitHub Actions security - helper-scripts

The required workflow patterns (least-priv permissions,
persist-credentials false, fork-PR guard, no direct interpolation of
`${{ github.event.* }}` into `run:`, SHA pinning, hard timeouts, inline
shell only when unavoidable) are documented once in the sibling repo:

  derivative-maker/agents/github-actions-security.md

Editors of `.github/workflows/*.yml` here must follow that doc verbatim.

Per-pin provenance lives next to the pin itself (a `## <release URL>`
plus `## > <SHA>` comment block above each `uses: ...@<sha>` and each
container `image:`). It is NOT duplicated here.
