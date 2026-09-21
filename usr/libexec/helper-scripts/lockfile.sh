#!/bin/bash

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## Lock file mechanism to prevent duplicate script instances, PER USER.
##
## Scope is per-user BY DESIGN -- system-wide (cross-user) mutual exclusion is
## out of purpose; kept simple. A resource that must be serialized across users
## is gated elsewhere (for example 'apt-get update' requires root), so a per-user
## lock is sufficient. The lock therefore lives in the caller's private per-user
## runtime directory (root-created, mode 0700), which also makes it immune to the
## /tmp symlink attack that a predictable, world-writable shared lock dir exposes.
##
## Two ways to use it:
##   * Source it to self-lock the sourcing script. Only one instance of the
##     script will be able to run at a time.
##   * Execute it as  'lockfile.sh <lock-key> -- <command> [args...]'  to run the
##     command under a per-key lock (skipping, non-zero, if the key is already
##     held).

## Based on flock man page.
## > [ "${FLOCKER}" != "${0}" ] && exec env FLOCKER="${0}" flock -en "${0}" "${0}" "$@" || :

## style-ok: no-strict -- sourced helper.

## style-ok: allow-exec -- process handoff is used here intentionally.

true "${BASH_SOURCE[0]}: START"

true "${BASH_SOURCE[0]}: INFO: FLOCKER: ${FLOCKER-}"

## Per-user lock directory (see the per-user-by-design note at the top). The lock
## never lives in /tmp. Prefer the caller's private per-user runtime dir (mode
## 0700, root-created -- fully isolated). Where none exists (e.g. a session-less
## root run) fall back to a per-user subdirectory of '/run/flocker', a
## root-provisioned base (tmpfiles.d, 1777 root:root): root owns the base, so
## unlike /tmp an unprivileged user cannot pre-create or symlink it.
flocker_runtime_dir="${XDG_RUNTIME_DIR:-/run/user/${EUID}}"
if [ -d "${flocker_runtime_dir}" ] && [ ! -L "${flocker_runtime_dir}" ]; then
  flocker_temp_folder="${flocker_runtime_dir}/flocker"
elif [ -d /run/flocker ] && [ ! -L /run/flocker ]; then
  flocker_temp_folder="/run/flocker/${EUID}"
else
  printf '%s\n' "$0: ERROR: no per-user runtime dir and '/run/flocker' is missing or a symlink; cannot create a lock directory!" 1>&2
  exit 1
fi
mkdir --parents -- "${flocker_temp_folder}"
## Belt-and-suspenders for the shared '/run/flocker' base: refuse a symlinked
## per-user dir another user could have pre-created (mkdir --parents follows it).
if [ -L "${flocker_temp_folder}" ]; then
  printf '%s\n' "$0: ERROR: refusing lock directory '${flocker_temp_folder}': it is a symlink!" 1>&2
  exit 1
fi

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
    ## Code duplication. Also in xtrace.bsh function shellopts_with_xtrace.
    ## This helper intentionally avoids sourcing dependencies.
    ## TODO: Do we need to avoid sourcing dependencies?
    case ":${SHELLOPTS-}:" in
      *:xtrace:*)
        flocker_shellopts="${SHELLOPTS-}"
        ;;
      *)
        flocker_shellopts="${SHELLOPTS-}:xtrace"
        ;;
    esac
    exec env SHELLOPTS="${flocker_shellopts}" FLOCKER="${0}" flock --exclusive --nonblock "${flocker_lockfile}" "${0}" "${@}"
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
