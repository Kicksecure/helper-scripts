#!/bin/bash

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

leaprun_exe="$(which leaprun)"
use_leaprun='no'
if [ -n "${leaprun_exe}" ] \
   && [ -f "/etc/privleapd/pid" ] \
   && [ -d "/proc/$(cat /etc/privleapd/pid)" ] \
   && [ -e "/etc/privleapd/comm/$(id -nu)" ]; then
   use_leaprun='yes'
fi
