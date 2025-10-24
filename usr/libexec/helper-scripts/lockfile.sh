#!/bin/bash

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## Supposed to be 'source'ed by other scripts.
## Not supposed to be executed (except during development).
## Lock file mechanism to prevent duplicate script instances across users

## Based on flock man page.
## > [ "${FLOCKER}" != "$0" ] && exec env FLOCKER="$0" flock -en "$0" "$0" "$@" || :

true "${BASH_SOURCE[0]}: START"

true "${BASH_SOURCE[0]}: INFO: FLOCKER: ${FLOCKER-}"

[[ -v TMP ]] || TMP="/tmp"
flocker_temp_folder="${TMP}/flocker-temp-folder"
mkdir --parents -- "${flocker_temp_folder}"

flocker_path_substituted="$(realpath -- "${0}")"
flocker_path_substituted="${flocker_path_substituted//\//_slash_}"
flocker_path_substituted="${flocker_path_substituted//./_dot_}"
flocker_lockfile="${flocker_temp_folder}/${flocker_path_substituted}"

if ! test -f "${flocker_lockfile}"; then
  touch -- "${flocker_lockfile}"
fi

if [ "${FLOCKER-}" != "$0" ]; then
  if [ -o xtrace ]; then
    true "${BASH_SOURCE[0]}: xtrace (set -x) is set."
    FLOCKER="$0" flock --verbose --exclusive --nonblock "${flocker_lockfile}" bash -x "${0}" "${@}" >/dev/null
  else
    true "${BASH_SOURCE[0]}: xtrace (set -x) is not set."
    exec env FLOCKER="$0" flock --verbose --exclusive --nonblock "${flocker_lockfile}" "${0}" "${@}" >/dev/null
  fi
fi

true "${BASH_SOURCE[0]}: END"
