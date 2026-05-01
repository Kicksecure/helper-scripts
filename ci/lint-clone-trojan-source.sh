#!/bin/bash

## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## AI-Assisted

## Clone the nickboucher/trojan-source corpus into ~/trojan-source.
## helper-scripts' ./run-tests scans against this corpus.
##
## Runs in .github/workflows/lint.yml between 'Build helper-scripts
## deb' and 'Run tests'. Split into its own step so that a clone
## failure is reported as a clearly-named step (exit 128 from git
## clone otherwise looks identical to a test-suite failure).
##
## Idempotent: removes any pre-existing trojan_source_dir so a partial
## clone from a previous failed run cannot trip us up.

set -o errexit
set -o nounset
set -o pipefail
set -o errtrace
set -o xtrace

## CI guard. Clobbers any pre-existing $HOME/trojan-source - that's
## fine in a CI container but surprising on a developer host. Refuse
## outside CI unless ALLOW_LOCAL=true is set explicitly.
if [ "${CI:-}" != "true" ] && [ "${ALLOW_LOCAL:-}" != "true" ]; then
  printf '%s\n' "${BASH_SOURCE[0]}: refusing to run outside CI (CI != 'true'). Set ALLOW_LOCAL=true to override." >&2
  exit 1
fi

trojan_source_dir="${HOME:-/root}/trojan-source"

## Diagnostic dump - if git clone fails, environment context is
## visible without log access.
printf '%s\n' "::group::pre-clone environment"
printf '%s\n' "HOME=${HOME:-<unset>}"
printf '%s\n' "trojan_source_dir=$trojan_source_dir"
printf '%s\n' "PWD=$PWD"
printf '%s\n' "USER=${USER:-<unset>}  EUID=$EUID"
which git || true
git --version || true
ls -la -- "$(dirname -- "$trojan_source_dir")" 2>/dev/null || true
printf '%s\n' "::endgroup::"

rm -rf -- "$trojan_source_dir"
git clone -- https://github.com/nickboucher/trojan-source "$trojan_source_dir"

printf '%s\n' "::group::post-clone status"
ls -la -- "$trojan_source_dir" | head
printf '%s\n' "::endgroup::"
