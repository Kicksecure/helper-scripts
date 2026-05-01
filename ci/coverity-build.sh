#!/bin/bash

## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## AI-Assisted

## Run cov-build over the source tree (Python source capture).
##
## --no-command + --fs-capture-search means "do not invoke a real
## build, just walk the filesystem and ingest source files". This is
## the documented Coverity approach for interpreted-only projects
## (Python here).
##
## Expects 'cov-build' to be on $PATH (set up by ci/coverity-download.sh
## via $GITHUB_PATH).

set -o errexit
set -o nounset
set -o pipefail
set -o errtrace

## CI guard. Requires cov-build on PATH (set up by coverity-download.sh).
## Refuse outside CI unless ALLOW_LOCAL=true is set explicitly.
if [ "${CI:-}" != "true" ] && [ "${ALLOW_LOCAL:-}" != "true" ]; then
  printf '%s\n' "${BASH_SOURCE[0]}: refusing to run outside CI (CI != 'true'). Set ALLOW_LOCAL=true to override." >&2
  exit 1
fi

cd -- "$(dirname -- "$(readlink -f -- "${BASH_SOURCE[0]}")")/.."

cov-build \
  --dir cov-int \
  --no-command \
  --fs-capture-search "$PWD" \
  --fs-capture-search-exclude-regex '/\.git(/|$)|/cov-analysis(/|$)|/cov-int(/|$)'

printf '%s\n' "::group::cov-int build summary"
tail -n 100 -- cov-int/build-log.txt 2>/dev/null || true
printf '%s\n' "::endgroup::"
