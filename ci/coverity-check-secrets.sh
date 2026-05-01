#!/bin/bash

## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## AI-Assisted

## Verify Coverity Scan secrets are present before the workflow
## attempts to use them. Fails fast with a clear ::error::
## annotation rather than letting the cov-build download fail with
## an opaque server-side error message.
##
## Expected env (from .github/workflows/coverity.yml):
##   COVERITY_TOKEN    - project token from scan.coverity.com
##   COVERITY_EMAIL    - notification email registered on the project
##   COVERITY_PROJECT  - project name as it appears in the URL

set -o errexit
set -o nounset
set -o pipefail
set -o errtrace

## CI guard. The Coverity workflow expects to find token/email/project
## in env. There is no sensible local invocation. Refuse outside CI
## unless ALLOW_LOCAL=true is set explicitly.
if [ "${CI:-}" != "true" ] && [ "${ALLOW_LOCAL:-}" != "true" ]; then
  printf '%s\n' "${BASH_SOURCE[0]}: refusing to run outside CI (CI != 'true'). Set ALLOW_LOCAL=true to override." >&2
  exit 1
fi

if [ -z "${COVERITY_TOKEN:-}" ]; then
  printf '%s\n' '::error::COVERITY_SCAN_TOKEN repository secret is not set. See .github/workflows/coverity.yml header for setup.' >&2
  exit 1
fi

if [ -z "${COVERITY_EMAIL:-}" ]; then
  printf '%s\n' '::error::COVERITY_SCAN_EMAIL repository secret is not set. See .github/workflows/coverity.yml header for setup.' >&2
  exit 1
fi

if [ -z "${COVERITY_PROJECT:-}" ]; then
  printf '%s\n' '::error::COVERITY_PROJECT repository variable is not set. See .github/workflows/coverity.yml header for setup.' >&2
  exit 1
fi

printf 'Coverity project: %s\n' "$COVERITY_PROJECT"
