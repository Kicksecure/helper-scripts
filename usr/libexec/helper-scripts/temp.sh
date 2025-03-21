#!/bin/bash

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

check_tempdir() {
  local id_of_user tmpdir_expected temp_file

  if [ -z "${TMPDIR+x}" ]; then
    printf "%s\n" "ERROR: TMPDIR variable is not set!" >&2
    return 1
  fi

  id_of_user="$(id --user)"
  tmpdir_expected="/tmp/user/${id_of_user}"
  true "TMPDIR: $TMPDIR"

  if [ "$TMPDIR" != "$tmpdir_expected" ]; then
    printf "%s\n" "ERROR: tmpdir_expected '$tmpdir_expected' does not match TMPDIR '$TMPDIR'!" >&2
    return 1
  fi

  if ! test -d "$TMPDIR"; then
    printf "%s\n" "ERROR: TMPDIR '$TMPDIR' does not exist!" >&2
    return 1
  fi

  if ! temp_file="$(mktemp)" ; then
    printf "%s\n" "ERROR: mktemp failed!" >&2
    return 1
  fi

  ## 'sponge' can cause error "mkstemp failed: No such file or directory" when $TMPDIR does not exist.
  if ! printf "%s\n" "test" | sponge "$temp_file" ; then
    printf "%s\n" "ERROR: Testing 'sponge' failed!" >&2
    return 1
  fi

  if ! safe-rm -f "$temp_file" ; then
    printf "%s\n" "ERROR: 'safe-rm -f $temp_file' failed!" >&2
    return 1
  fi

  return 0
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  true "$0: START"
  set -o errexit
  set -o nounset
  set -o errtrace
  set -o pipefail
  check_tempdir
  true "$0: END"
fi
