#!/bin/bash

## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## Authored by Claude (Anthropic).

## Install Atheris and its build prerequisites for the fuzz workflow
## (.github/workflows/fuzz.yml).
##
## Atheris is not in Debian's archive. We install via pip with
## --break-system-packages. Publisher / trust root: Google (Atheris
## is part of Google's OSS-Fuzz toolchain).
##   https://github.com/google/atheris (canonical source)
##   https://pypi.org/project/atheris/ (distribution channel)

set -o errexit
set -o nounset
set -o pipefail
set -o errtrace

## CI guard. sudo apt-get + 'pip install --break-system-packages' on
## a developer host is dangerous. Refuse outside CI unless
## ALLOW_LOCAL=true is set explicitly.
if [ "${CI:-}" != "true" ] && [ "${ALLOW_LOCAL:-}" != "true" ]; then
  printf '%s\n' "${BASH_SOURCE[0]}: refusing to run outside CI (CI != 'true'). Set ALLOW_LOCAL=true to override." >&2
  exit 1
fi

sudo apt-get update -qq
sudo apt-get install -y --no-install-recommends \
  python3 python3-pip python3-hypothesis

python3 -m pip install --break-system-packages atheris

python3 -c "import atheris; print(f'atheris {atheris.__version__}')"
