#!/bin/bash

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## Supposed to be 'source'ed by other scripts.
## Not supposed to be executed (except during development).
## Lock file mechanism to prevent duplicate script instances across users

## Based on flock man page.
## > [ "${FLOCKER}" != "${0}" ] && exec env FLOCKER="${0}" flock -en "${0}" "${0}" "$@" || :

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

if [ "${FLOCKER-}" != "${0}" ]; then
  true "${BASH_SOURCE[0]}: INFO: FLOCKER set to self: no"

  ## Using 'flock' with option '--verbose' but hiding stdout for the purpose of showing
  ## 'flock: failed to get lock' error message, if applicable.
  ## The error message is not perfectly atomic.
  flock --verbose --exclusive --nonblock "${flocker_lockfile}" /usr/bin/true >/dev/null
  ## But if we were to use '--verbose' below, then 'flock' would always add verbose
  ## output even in case it was possible to acquire a lock.

  if test -o xtrace; then
    ## XXX: Might add a superfluous ':xtrace'.
    exec env SHELLOPTS="${SHELLOPTS-}:xtrace" FLOCKER="${0}" flock --exclusive --nonblock "${flocker_lockfile}" "${0}" "${@}"
  else
    exec env FLOCKER="${0}" flock --exclusive --nonblock "${flocker_lockfile}" "${0}" "${@}"
  fi
  ## Never reached due to 'exec' above.
fi

true "${BASH_SOURCE[0]}: INFO: FLOCKER set to self: yes"

true "${BASH_SOURCE[0]}: END"
