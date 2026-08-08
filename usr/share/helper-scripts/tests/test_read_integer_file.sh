#!/bin/bash

## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## AI-Assisted

## Regression test for read_integer_file, which reads a number back out of a
## state file.
##
## THE BUG: the read went through 'stcat -- "${target_file}"'. stcat takes
## EVERY argument as a path, so it read the '--' separator itself as a
## filename and died with FileNotFoundError. read_integer_file then reported
## "Cannot stcat target file" for a file that was present and readable, and
## four of tb-updater's e2e scenarios failed on it -- all of them the ones
## that read a cached signature timestamp back.
##
## R-062 is why it was added: the separator is right for tools that accept
## one. It is a bug for tools that do not, which is the rule's negative half.
## pre-push-static now denylists 'stcat --'; this test pins the runtime side.
##
## Tests the INSTALLED library, not the checkout: a self-relative source would
## pass against a stale install, which is the failure mode this suite exists
## to catch.

set -o errexit
set -o nounset
set -o pipefail
set -o errtrace
shopt -s inherit_errexit
shopt -s shift_verbose

[ -v TMP ] || TMP=/tmp

if ! test -r /usr/libexec/helper-scripts/strings.bsh ; then
   printf '%s\n' "FATAL: /usr/libexec/helper-scripts/strings.bsh is not installed" >&2
   exit 1
fi

# shellcheck source=../../../libexec/helper-scripts/strings.bsh
# shellcheck disable=SC1091
source /usr/libexec/helper-scripts/strings.bsh

if ! test -x /usr/bin/stcat ; then
   printf '%s\n' "FATAL: stcat is not installed; this test cannot exercise the read path" >&2
   exit 1
fi

test_dir="$(mktemp --directory -- "${TMP}/read-integer-file-test.XXXXXX")"

test_cleanup_handler() {
   safe-rm --recursive --force -- "${test_dir}"
}

trap test_cleanup_handler EXIT

fail=0

check_reads() {
   local description contents expected actual rc

   description="$1"
   contents="$2"
   expected="$3"

   printf '%s\n' "${contents}" >"${test_dir}/value"
   rc=0
   actual="$(read_integer_file "${test_dir}/value" 1 4294967295 2>/dev/null)" || rc=$?
   if [ "${rc}" -ne 0 ]; then
      printf '%s\n' "FAIL: ${description} -- read_integer_file returned ${rc}"
      fail=1
      return 0
   fi
   if [ ! "${actual}" = "${expected}" ]; then
      printf '%s\n' "FAIL: ${description} -- expected ${expected}, got ${actual}"
      fail=1
      return 0
   fi
   printf '%s\n' "PASS: ${description}"
}

check_rejects() {
   local description contents rc

   description="$1"
   contents="$2"

   printf '%s\n' "${contents}" >"${test_dir}/value"
   rc=0
   read_integer_file "${test_dir}/value" 1 4294967295 >/dev/null 2>&1 || rc=$?
   if [ "${rc}" -eq 0 ]; then
      printf '%s\n' "FAIL: ${description} -- accepted"
      fail=1
      return 0
   fi
   printf '%s\n' "PASS: ${description}"
}

## The case that broke: an ordinary unix timestamp, the shape tb-updater
## stores in last_used_gpg_bash_lib_output_signed_on_unixtime.
check_reads 'a unix timestamp is read back' '1786185710' '1786185710'
check_reads 'the lower bound itself is accepted' '1' '1'
check_reads 'the upper bound itself is accepted' '4294967295' '4294967295'

check_rejects 'a non-numeric value' 'not-a-number'
check_rejects 'a value below the lower bound' '0'
check_rejects 'a value above the upper bound' '4294967296'

## An absent file must fail rather than return an empty string that a caller
## would then use in arithmetic.
rc=0
read_integer_file "${test_dir}/absent" 1 4294967295 >/dev/null 2>&1 || rc=$?
if [ "${rc}" -eq 0 ]; then
   printf '%s\n' "FAIL: an absent file was accepted"
   fail=1
else
   printf '%s\n' "PASS: an absent file is rejected"
fi

if [ "${fail}" -ne 0 ]; then
   printf '%s\n' "" "FAILED"
   exit 1
fi
printf '%s\n' "" "OK"
