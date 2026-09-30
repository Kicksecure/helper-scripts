#!/bin/bash

## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## AI-Assisted

## ClusterFuzzLite build script. Invoked inside the OSS-Fuzz
## base-builder-python container by the ClusterFuzzLite tooling.
##
## Standard OSS-Fuzz contract:
##   - $SRC      - source root (we COPY the repo here in the Dockerfile)
##   - $OUT      - output directory; harnesses go here
##   - compile_python_fuzzer - OSS-Fuzz helper that wraps a python
##                              harness into a runnable executable
##                              and copies it to $OUT/
##
## SRC and OUT are exported by the OSS-Fuzz base-builder container, not this
## script, so shellcheck cannot see their assignment.
# shellcheck disable=SC2154

set -o errexit
set -o nounset
set -o pipefail
set -o errtrace
shopt -s inherit_errexit
shopt -s shift_verbose
export LC_ALL=C

## NOTE: no CI-guard here. This script is invoked by ClusterFuzzLite
## inside the OSS-Fuzz base-builder container; it does not see the
## GitHub Actions CI=true env var. The trust boundary is the container
## itself, not this script.

cd -- "${SRC}/helper-scripts"

## Make our Python packages importable inside the harnesses.
export PYTHONPATH="${SRC}/helper-scripts/usr/lib/python3/dist-packages${PYTHONPATH+:${PYTHONPATH}}"

## Shared CFLite smoke-run guard (single source of truth in dist-ai; the
## Dockerfile clones it to $SRC/dist-ai). It bounds-runs each compiled fuzzer
## with PYTHONPATH + every *_REPO override unset and FAILs the build on a
## non-zero exit -- catching a frozen-bundle SystemExit(77) silent skip that
## would otherwise pass vacuously.
# shellcheck disable=SC1090,SC1091
source "${SRC}/dist-ai/usr/share/clusterfuzzlite-lib/smoke-run.bash"

## Wrap each fuzz/fuzz_*.py harness for OSS-Fuzz's Python runtime, then smoke-run
## it to catch a frozen-bundle SILENT SKIP.
for harness in fuzz/fuzz_*.py; do
  name="$(basename -- "${harness}" .py)"
  compile_python_fuzzer "${harness}"
  cflite_smoke_run_fuzzers "${name}"
  printf 'compiled %s\n' "${name}"
done
