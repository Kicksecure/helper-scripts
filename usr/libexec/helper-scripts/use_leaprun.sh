#!/bin/bash

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

use_leaprun='no'

if ! leaprun_exe="$(command -v leaprun)"; then
   echo "$0: WARNING: leaprun executable cannot be found, cannot use privleap."
elif ! [ -f "/run/privleapd/pid" ]; then
   echo "$0: WARNING: Cannot check if privleapd is not running, cannot use privleap."
elif ! [ -d "/proc/$(cat /run/privleapd/pid)" ]; then
   echo "$0: WARNING: privleapd is not running, cannot use privleap."
elif ! [ -e "/run/privleapd/comm/$(id -nu)" ]; then
   echo "$0: WARNING: Cannot communicate with privleapd, cannot use privleap."
else
   use_leaprun='yes'
fi
