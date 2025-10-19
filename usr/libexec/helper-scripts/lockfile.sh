#!/bin/bash

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## Supposed to be 'source'ed by other scripts.
## Not supposed to be executed (except during development).
## Lock file mechanism to prevent duplicate script instances across users

my_id="$(id --user)"
SCRIPT_NAME="$(basename -- "$0")"
LOCKDIR="/run/user/${my_id}/lockfile"
PIDFILE="${LOCKDIR}/${SCRIPT_NAME}.pid"
LOCKFILE="${LOCKDIR}/${SCRIPT_NAME}.lock"

cleanup_lockfile() {
  safe-rm -f -- "$PIDFILE"
  ## Bad idea?
  #safe-rm -f -- "$LOCKFILE"
}

command -v safe-rm >/dev/null
command -v stcat >/dev/null
command -v overwrite >/dev/null

if ! mkdir --parents -- "$LOCKDIR"; then
  printf '%s\n' "$0: ERROR: Failed to create lock directory '$LOCKDIR'. Check permissions."
  exit 1
fi

if [ -d "$LOCKDIR" ]; then
  if [[ ! -r "$LOCKDIR" || ! -w "$LOCKDIR" || ! -x "$LOCKDIR" ]]; then
    printf '%s\n' "$0: ERROR: No rwx access to lock directory '$LOCKDIR'. Check permissions."
    exit 1
  fi
fi

if [ -e "$PIDFILE" ]; then
  if ! [ -r "$PIDFILE" ] || ! [ -w "$PIDFILE" ]; then
    printf '%s\n' "$0: ERROR: Cannot read/write to lock file '$PIDFILE'. Check permissions."
    exit 1
  fi

  LOCK_PID=$(stcat "$PIDFILE" 2>/dev/null)
  if [ -z "$LOCK_PID" ]; then
    printf '%s\n' "$0: WARNING: Lock file exists but is empty. Removing stale lock file."
    safe-rm -f -- "$PIDFILE"
  elif ! [[ "$LOCK_PID" =~ ^[0-9]+$ ]]; then
    printf '%s\n' "$0: WARNING: Lock file contains invalid PID. Removing stale lock file."
    safe-rm -f -- "$PIDFILE"
  elif kill -0 -- "$LOCK_PID" 2>/dev/null; then
    printf '%s\n' "$0: ERROR: Another instance of '${SCRIPT_NAME}' is already running with PID '$LOCK_PID'."
    exit 1
  else
    printf '%s\n' "$0: WARNING: Lock file contains PID '$LOCK_PID', but no process is running. Removing stale lock file."
    safe-rm -f -- "$PIDFILE"
  fi
fi

trap cleanup_lockfile EXIT

if ! flock --nonblock "$LOCKFILE" overwrite "$PIDFILE" "$$" >/dev/null ; then
  trap '' EXIT
  exit 1
fi

## Debugging.
# if ! flock --verbose --exclusive --nonblock "$LOCKFILE" sleep 10 ; then
#   trap '' EXIT
#   exit 1
# fi
