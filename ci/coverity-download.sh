#!/bin/bash

## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## AI-Assisted

## Download the Coverity Scan build tool and verify it.
##
## scan.coverity.com gates the download on a valid project token, so
## an attacker without the token cannot fetch the same binary we run.
##
## Two-layer integrity check:
##   1. md5 from Coverity's md5=1 endpoint - rules out CDN / mirror
##      tampering against the same tokenless attacker (Coverity has not
##      yet published a stronger digest endpoint as of 2026-04).
##   2. sha256 hard-pin from .coverity-tool-sha256.expected (committed
##      to the repository) - protects against md5 collision attacks
##      and against the (more theoretical) scan.coverity.com side
##      compromise. If the file exists, the sha256 of the download
##      MUST match the pinned value or the script fails closed.
##
## Updating the pin (when Synopsys publishes a new cov-build):
##   1. Run the workflow with no .coverity-tool-sha256.expected file.
##   2. Read the printed sha256 from the workflow log.
##   3. Verify it independently (e.g. by running the same command on a
##      second host with a different token) before committing.
##   4. Commit it to .coverity-tool-sha256.expected.
##
## On success, prints the absolute path to the cov-analysis bin
## directory so the caller can append it to the workflow's GITHUB_PATH.
##
## Expected env (from .github/workflows/coverity.yml):
##   COVERITY_TOKEN
##   COVERITY_PROJECT

set -o errexit
set -o nounset
set -o pipefail
set -o errtrace

## CI guard. Downloads a token-gated binary and writes it to disk.
## Refuse outside CI unless ALLOW_LOCAL=true is set explicitly.
if [ "${CI:-}" != "true" ] && [ "${ALLOW_LOCAL:-}" != "true" ]; then
  printf '%s\n' "${BASH_SOURCE[0]}: refusing to run outside CI (CI != 'true'). Set ALLOW_LOCAL=true to override." >&2
  exit 1
fi

cd -- "$(dirname -- "$(readlink -f -- "${BASH_SOURCE[0]}")")/.."

mkdir -p -- cov-analysis

## Tarball
curl \
  --silent \
  --show-error \
  --fail \
  --form "token=${COVERITY_TOKEN}" \
  --form "project=${COVERITY_PROJECT}" \
  --output cov-analysis-linux64.tgz \
  https://scan.coverity.com/download/linux64

## md5 reference value (Coverity's only published digest as of 2026-04)
curl \
  --silent \
  --show-error \
  --fail \
  --form "token=${COVERITY_TOKEN}" \
  --form "project=${COVERITY_PROJECT}" \
  --form 'md5=1' \
  --output cov-analysis-linux64.md5 \
  https://scan.coverity.com/download/linux64

## Layer 1: md5 verification (against scan.coverity.com).
actual_md5="$(md5sum -- cov-analysis-linux64.tgz | awk '{print $1}')"
expected_md5="$(awk '{print $1}' cov-analysis-linux64.md5)"

if [ "$actual_md5" != "$expected_md5" ]; then
  printf '%s\n' "::error::Coverity tool md5 mismatch: got $actual_md5, expected $expected_md5" >&2
  exit 1
fi
printf 'Coverity tool md5 verified: %s\n' "$actual_md5"

## Layer 2: sha256 hard-pin (against repo-committed expected value).
actual_sha256="$(sha256sum -- cov-analysis-linux64.tgz | awk '{print $1}')"
printf 'Coverity tool sha256: %s\n' "$actual_sha256"

sha256_pin_file='.coverity-tool-sha256.expected'
if [ -f "$sha256_pin_file" ]; then
  expected_sha256="$(awk 'NF && $1 !~ /^#/ {print $1; exit}' -- "$sha256_pin_file")"
  if [ -z "$expected_sha256" ]; then
    printf '%s\n' "::error::$sha256_pin_file exists but contains no sha256 value." >&2
    exit 1
  fi
  if [ "$actual_sha256" != "$expected_sha256" ]; then
    printf '%s\n' "::error::Coverity tool sha256 mismatch: got $actual_sha256, expected $expected_sha256 (from $sha256_pin_file)" >&2
    exit 1
  fi
  printf 'Coverity tool sha256 hard-pin verified: %s\n' "$actual_sha256"
else
  printf '%s\n' "::warning::No $sha256_pin_file in repo; only md5 was verified. After verifying the printed sha256 independently, commit it to pin against md5-collision attacks."
fi

tar -xzf cov-analysis-linux64.tgz -C cov-analysis --strip-components=1 --
rm -f -- cov-analysis-linux64.tgz cov-analysis-linux64.md5

## Print the bin path so the workflow caller can append to $GITHUB_PATH.
printf '%s\n' "$PWD/cov-analysis/bin"
