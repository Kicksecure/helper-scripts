#!/bin/bash

## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## AI-Assisted

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

## The suite includes permission-based rejection tests (e.g. 'append' refusing
## an unwritable parent dir). Those are no-ops under root: CAP_DAC_OVERRIDE lets
## root write regardless of the mode bits, so os.access(dir, W_OK) returns true
## and the rejection never fires -- the test then false-fails (got 0, want 1).
## CI container jobs run as root, so run the whole suite as a throwaway NON-ROOT
## user, which exercises the real rejection path. No test needs root. run-tests
## does read the trojan-source corpus from the runner's HOME, so it is copied to
## the test user's HOME below.
##
## Gated on CI too, not EUID alone: this block creates a system user and
## 'chown --recursive's the checkout, which is fine in the ephemeral CI
## container but would be a destructive surprise on a dev host running
## 'sudo ALLOW_LOCAL=true ./ci/lint-tests.sh'. Locally, just run as-is.
if [ "${EUID}" -eq 0 ] && [ "${CI:-}" = "true" ]; then
  test_user='hs-tester'
  id -- "${test_user}" >/dev/null 2>&1 \
    || useradd --create-home --shell /bin/bash -- "${test_user}"
  ## git refuses a repo owned by a different user ("dubious ownership"), so hand
  ## the whole checkout to the test user; pytest/black/pylint/mypy read from it
  ## and the tests write only to their own /tmp TemporaryDirectory.
  chown --recursive -- "${test_user}:${test_user}" .
  ## run-tests reads "${HOME}/trojan-source" (the unicode-testscript corpus) and
  ## exits 1 if it is absent. The previous CI step cloned it into root's HOME
  ## (ci/lint-clone-trojan-source.sh uses "${HOME:-/root}"), but the test user's
  ## HOME differs, so give it its own readable copy.
  src_corpus="${HOME:-/root}/trojan-source"
  if [ -d "${src_corpus}" ]; then
    cp --recursive -- "${src_corpus}" "/home/${test_user}/trojan-source"
    chown --recursive -- "${test_user}:${test_user}" "/home/${test_user}/trojan-source"
  fi
  exec runuser --user "${test_user}" -- \
    env HOME="/home/${test_user}" CI="${CI:-true}" ./run-tests
fi

./run-tests
