#!/bin/bash

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## Two ways to use it:
##   * SOURCE it to self-lock the sourcing script: only one instance runs at a
##     time (keyed by the script's own path, or by LOCK_NAME).
##   * EXECUTE it as  'lockfile.sh <lock-key> -- <command> [args...]'  to run the
##     command under a PER-KEY lock (skipping, non-zero, if the key is already
##     held) -- a generic 'run this under a per-key lock' front-end. An executed
##     run with NO arguments keeps the old dev self-lock behaviour.
## Lock file mechanism to prevent duplicate script instances across users

## Based on flock man page.
## > [ "${FLOCKER}" != "${0}" ] && exec env FLOCKER="${0}" flock -en "${0}" "${0}" "$@" || :

## style-ok: no-strict -- sourced flock lock helper; deliberately sets no
## set-options so it imposes none on the sourcing script.

## style-ok: allow-exec -- process handoff is used here intentionally.

true "${BASH_SOURCE[0]}: START"

true "${BASH_SOURCE[0]}: INFO: FLOCKER: ${FLOCKER-}"

[[ -v TMP ]] || TMP="/tmp"
flocker_temp_folder="${TMP}/flocker-temp-folder"
if ! [ -d "${TMP}" ]; then
  printf '%s\n' "$0: ERROR: Could not create lock file directory at '${flocker_temp_folder}', because '${TMP}' does not exist or is not a directory!" 1>&2
  exit 1
fi
mkdir --parents -- "${flocker_temp_folder}"

## Wrap-mode setup: an EXECUTED run with arguments treats $1 as the lock key and
## runs the rest as a command under that key's lock (the run happens on the
## locked pass, below). A SOURCED use (BASH_SOURCE != $0) or an executed no-arg
## dev run leaves this off, keeping the self-lock behaviour below.
lockfile_wrap="no"
if [ "${BASH_SOURCE[0]}" = "${0}" ] && [ "${#}" -ge 1 ]; then
  lockfile_wrap="yes"
  LOCK_NAME="${1}"
fi

## The lock key defaults to this script's own path. A caller that runs the same
## script concurrently for different keys can set LOCK_NAME to lock per key
## instead.
if [ -n "${LOCK_NAME-}" ]; then
  flocker_key="${LOCK_NAME}"
else
  flocker_key="$(realpath -- "${0}")"
fi

flocker_path_substituted="${flocker_key//_/_underscore_}"
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

## If we get this far, we're in wrap mode. The above code will have re-executed
## this script with the lock held, so now we just need to hand off to the
## target command.
if [ "${lockfile_wrap}" = "yes" ]; then
  shift # Get rid of the lock key name
  if [ "${#}" -ge 1 ] && [ "${1}" = "--" ]; then
    shift # We support end-of-options even though we don't have any options
  fi
  if [ "${#}" -lt 1 ]; then
    printf '%s\n' "${0}: ERROR: usage: ${0} <lock-key> -- <command> [args...]" 1>&2
    exit 2
  fi
  unset LOCK_NAME FLOCKER
  exec -- "${@}"
fi

true "${BASH_SOURCE[0]}: INFO: FLOCKER set to self: yes"

true "${BASH_SOURCE[0]}: END"
