#!/bin/bash

## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## Authored by Claude (Anthropic).

## Build the helper-scripts Debian package and install the resulting
## .deb so the test suite can exercise the deb-installed paths.
##
## Runs in .github/workflows/lint.yml after 'Install linters' and
## before 'Run tests'. Standalone-runnable from a checkout for parity.

set -o errexit
set -o nounset
set -o pipefail
set -o errtrace
set -o xtrace

## CI guard. dpkg-buildpackage + apt-get install modify system state.
## Refuse to run outside CI unless ALLOW_LOCAL=true is set explicitly.
if [ "${CI:-}" != "true" ] && [ "${ALLOW_LOCAL:-}" != "true" ]; then
  printf '%s\n' "${BASH_SOURCE[0]}: refusing to run outside CI (CI != 'true'). Set ALLOW_LOCAL=true to override." >&2
  exit 1
fi

cd -- "$(dirname -- "$(readlink -f -- "${BASH_SOURCE[0]}")")/.."

dpkg-buildpackage -b -i -us -uc

apt-get install -y -- ../helper-scripts*.deb
