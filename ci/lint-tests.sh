#!/bin/bash

## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## Authored by Claude (Anthropic).

## Run the helper-scripts test suite (./run-tests).
##
## Runs in .github/workflows/lint.yml after 'Clone trojan-source
## corpus' (which populates ~/trojan-source). Standalone-runnable
## from a checkout for parity, provided ~/trojan-source is present.

set -o errexit
set -o nounset
set -o pipefail
set -o errtrace
set -o xtrace

## CI guard. ./run-tests itself is safe to run locally, but this
## wrapper assumes the lint workflow's environment (apt deps installed,
## ~/trojan-source populated). Refuse outside CI unless overridden.
if [ "${CI:-}" != "true" ] && [ "${ALLOW_LOCAL:-}" != "true" ]; then
  printf '%s\n' "${BASH_SOURCE[0]}: refusing to run outside CI (CI != 'true'). Set ALLOW_LOCAL=true to override." >&2
  exit 1
fi

cd -- "$(dirname -- "$(readlink -f -- "${BASH_SOURCE[0]}")")/.."

## Diagnostic dump - if ./run-tests fails, this gives the maintainer
## the env state needed to reproduce.
printf '%s\n' "::group::tests environment"
printf '%s\n' "HOME=${HOME:-<unset>}"
printf '%s\n' "PWD=$PWD"
printf '%s\n' "USER=${USER:-<unset>}  EUID=$EUID"
ls -la -- "${HOME:-/root}/trojan-source" 2>/dev/null | head || true
printf '%s\n' "::endgroup::"

./run-tests
