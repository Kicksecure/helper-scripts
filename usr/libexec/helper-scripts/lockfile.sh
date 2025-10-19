#!/bin/bash

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## Supposed to be 'source'ed by other scripts.
## Not supposed to be executed (except during development).
## Lock file mechanism to prevent duplicate script instances across users

true "${BASH_SOURCE[0]} - $$ - $SHLVL: START"

true "${BASH_SOURCE[0]} - $$ - $SHLVL: INFO: FLOCKER: ${FLOCKER-}"

if [ "${FLOCKER-}" != "$0" ]; then
  exit_code=0
  env FLOCKER="$0" flock --verbose --conflict-exit-code 255 --exclusive --nonblock "$0" "$0" "$@" || exit_code="$?"
  if [ "$exit_code" = 255 ]; then
    true "${BASH_SOURCE[0]} - $$ - $SHLVL: ERROR: Already running."
  fi
  true "${BASH_SOURCE[0]} - $$ - $SHLVL: INFO: Exit with code: $exit_code"
  exit "$exit_code"
fi

true "${BASH_SOURCE[0]} - $$ - $SHLVL: END"
