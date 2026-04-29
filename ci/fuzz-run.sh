#!/bin/bash

## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## Authored by Claude (Anthropic).

## Run every fuzz/fuzz_*.py harness for a bounded per-harness time
## budget ($MAX_TOTAL_TIME seconds; default 60). Aggregates exit
## codes so a single crash does not skip the remaining harnesses.
##
## Run a single harness locally:
##     python3 fuzz/fuzz_stdisplay.py -max_total_time=60
##
## Run all harnesses locally as the workflow does:
##     MAX_TOTAL_TIME=60 bash ci/fuzz-run.sh

set -o nounset
set -o errtrace
set -o pipefail
## NOT errexit: a crash in one harness should not skip the others.

## CI guard. The harnesses are safe to run locally (they just call
## python3), but this wrapper assumes the workflow's environment
## (atheris on PYTHONPATH, etc.). Refuse outside CI unless overridden.
if [ "${CI:-}" != "true" ] && [ "${ALLOW_LOCAL:-}" != "true" ]; then
  printf '%s\n' "${BASH_SOURCE[0]}: refusing to run outside CI (CI != 'true'). Set ALLOW_LOCAL=true to override." >&2
  exit 1
fi

cd -- "$(dirname -- "$(readlink -f -- "${BASH_SOURCE[0]}")")/.."

export PYTHONPATH="${PWD}/usr/lib/python3/dist-packages${PYTHONPATH+:${PYTHONPATH}}"

## Some helper-scripts modules use Python 3.12+ f-string syntax. CI's
## ubuntu-latest python3 is 3.12+; on developer hosts running an older
## python3, override:
##     PYTHON3=python3.13 bash ci/fuzz-run.sh
python3="${PYTHON3:-python3}"

max_total_time="${MAX_TOTAL_TIME:-60}"

declare -i overall_rc=0
declare -i harnesses_run=0
declare -i harnesses_failed=0

shopt -s nullglob
for harness in fuzz/fuzz_*.py; do
  harnesses_run=$(( harnesses_run + 1 ))
  printf '%s\n' "::group::${harness} (${max_total_time}s)"
  rc=0
  "${python3}" "${harness}" \
    -max_total_time="${max_total_time}" \
    -timeout=10 \
    -rss_limit_mb=2048 \
    || rc=$?
  printf '%s\n' "::endgroup::"
  if [ "${rc}" -ne 0 ]; then
    harnesses_failed=$(( harnesses_failed + 1 ))
    overall_rc="${rc}"
    printf '%s\n' "::error::${harness} exited ${rc}"
  fi
done
shopt -u nullglob

printf '\n'
if [ "${overall_rc}" -eq 0 ]; then
  printf 'PASSED: %d harnesses\n' "${harnesses_run}"
else
  printf 'FAILED: %d / %d harnesses\n' "${harnesses_failed}" "${harnesses_run}"
fi

exit "${overall_rc}"
