#!/bin/bash

## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## Authored by Claude (Anthropic).

## Submit cov-int output to Coverity Scan.
##
## Expected env (from .github/workflows/coverity.yml):
##   COVERITY_TOKEN
##   COVERITY_EMAIL
##   COVERITY_PROJECT
##   GITHUB_SHA          - identifies the snapshot in Coverity
##   GITHUB_RUN_NUMBER   - human-readable run identifier
##   GITHUB_REF_NAME     - branch / tag name

set -o errexit
set -o nounset
set -o pipefail
set -o errtrace

## CI guard. Submits to scan.coverity.com using a repo secret.
## Refuse outside CI unless ALLOW_LOCAL=true is set explicitly.
if [ "${CI:-}" != "true" ] && [ "${ALLOW_LOCAL:-}" != "true" ]; then
  printf '%s\n' "${BASH_SOURCE[0]}: refusing to run outside CI (CI != 'true'). Set ALLOW_LOCAL=true to override." >&2
  exit 1
fi

cd -- "$(dirname -- "$(readlink -f -- "${BASH_SOURCE[0]}")")/.."

tar -czf cov-int.tgz -- cov-int

curl --silent --show-error --fail \
  --form "token=${COVERITY_TOKEN}" \
  --form "email=${COVERITY_EMAIL}" \
  --form "file=@cov-int.tgz" \
  --form "version=${GITHUB_SHA:-unknown}" \
  --form "description=GHA run ${GITHUB_RUN_NUMBER:-unknown} on ${GITHUB_REF_NAME:-unknown}" \
  "https://scan.coverity.com/builds?project=${COVERITY_PROJECT}"

printf '\n'
printf '%s\n' "Submission accepted by scan.coverity.com."
printf '%s\n' "Results will appear at:"
printf '  %s\n' "https://scan.coverity.com/projects/${COVERITY_PROJECT}"
