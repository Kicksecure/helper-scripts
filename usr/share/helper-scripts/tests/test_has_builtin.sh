#!/bin/bash

## Copyright (C) 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## 'has' is the R-090 replacement for 'command -v', so it has to succeed for
## everything 'command -v' succeeds for -- including shell builtins, where
## 'command -v' prints a bare word instead of a path.

set -o errexit
set -o nounset
set -o pipefail
set -o errtrace
shopt -s inherit_errexit
shopt -s shift_verbose

error_handler() {
   local exit_code="$?"
   printf '%s\n' "ERROR: exit_code: ${exit_code} | BASH_COMMAND: ${BASH_COMMAND}"
   exit 1
}

trap error_handler ERR

## Sources the INSTALLED has.sh, not a copy resolved relative to this file.
## A self-relative source validates the checkout and passes even when the
## deployed copy is stale, which is exactly the failure it must be able to
## catch -- it reported 7/7 against a broken install once already.
has_sh_path="/usr/libexec/helper-scripts/has.sh"

if ! test -r "${has_sh_path}" ; then
   printf '%s\n' "ERROR: '${has_sh_path}' not readable; install helper-scripts first." >&2
   exit 1
fi

## The source= directive points at the in-tree copy purely so shellcheck can
## resolve the file statically. It does not affect what is sourced at runtime,
## which is the INSTALLED path above -- that distinction is the whole point.
# shellcheck source=../../../libexec/helper-scripts/has.sh
source "${has_sh_path}"

tests_total=0
tests_failed=0

check_has_succeeds() {
   local label="$1"
   shift
   tests_total=$(( tests_total + 1 ))
   if has "$@" ; then
      printf '%s\n' "PASS: ${label}"
   else
      printf '%s\n' "FAIL: ${label}: 'has $*' returned non-zero"
      tests_failed=$(( tests_failed + 1 ))
   fi
}

check_has_fails() {
   local label="$1"
   shift
   tests_total=$(( tests_total + 1 ))
   if has "$@" ; then
      printf '%s\n' "FAIL: ${label}: 'has $*' unexpectedly returned zero"
      tests_failed=$(( tests_failed + 1 ))
   else
      printf '%s\n' "PASS: ${label}"
   fi
}

## The regression: 'command -v printf' prints 'printf', and testing that with
## '-x' resolved it as a relative path in the cwd.
check_has_succeeds "builtin: printf" printf
check_has_succeeds "builtin: cd" cd
check_has_succeeds "builtin: test" test

## An external command still resolves to an absolute path and is still checked.
check_has_succeeds "external: cat" cat

## Several names at once, mixing a builtin and an external command.
check_has_succeeds "mixed builtin and external" printf cat

## A name that does not exist anywhere must still fail.
check_has_fails "absent command" this-command-does-not-exist-12345

## A builtin must not be confused with a same-named file in the cwd. Running
## from a directory that contains no such file is the point: before the fix
## 'has printf' depended on the current directory's contents.
check_has_fails "absent, mixed with a builtin" printf this-command-does-not-exist-12345

printf '%s\n' "---"
printf '%s\n' "${tests_total} run, $(( tests_total - tests_failed )) pass, ${tests_failed} fail, 0 skip"

if [ "${tests_failed}" != "0" ]; then
   exit 1
fi
