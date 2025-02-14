#!/bin/bash

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

leaprun_useable_test() {
   use_leaprun='no'

   if ! leaprun_exe="$(command -v leaprun)"; then
      echo "$0: WARNING: leaprun executable cannot be found. Cannot use privleap."
      return 0
   fi

   if ! [ -f "/run/privleapd/pid" ]; then
      echo "$0: WARNING: Cannot check if privleapd is not running. Cannot use privleap."
      return 0
   fi

   local privleap_pid
   if ! privleap_pid="$(cat /run/privleapd/pid)"; then
      echo "$0: WARNING: Failed to execute 'cat /run/privleapd/pid'. Cannot use privleap."
      return 0
   fi

   if ! [ -d "/proc/${privleap_pid}" ]; then
      echo "$0: WARNING: privleapd is not running. Folder '/proc/${privleap_pid}' does not exist. Cannot use privleap."
      return 0
   fi

   local my_user_id
   if ! my_user_id="$(id --name --user)"; then
      echo "$0: WARNING: Failed to execute 'id --name --user'. Cannot use privleap."
      return 0
   fi

   if ! [ -e "/run/privleapd/comm/${my_user_id}" ]; then
      echo "$0: WARNING: Cannot communicate with privleapd. File '/run/privleapd/comm/${my_user_id}' does not exist. Cannot use privleap."
      return 0
   fi

   use_leaprun='yes'
}

leaprun_useable_test
