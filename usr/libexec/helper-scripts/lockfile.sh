#!/bin/bash

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## Supposed to be 'source'ed by other scripts.
## Not supposed to be executed (except during development).
## Lock file mechanism to prevent duplicate script instances across users

true "${BASH_SOURCE[0]}: START"

true "${BASH_SOURCE[0]}: INFO: FLOCKER: ${FLOCKER-}"

if [ "${FLOCKER-}" != "$0" ]; then
  exec env FLOCKER="$0" flock --verbose --exclusive --nonblock "$0" "$0" "$@"
fi

true "${BASH_SOURCE[0]}: END"
