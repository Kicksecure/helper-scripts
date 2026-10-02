#!/bin/bash

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

# shellcheck source=./strings.bsh
source "${HELPER_SCRIPTS_PATH:-}"/usr/libexec/helper-scripts/strings.bsh

leaprun_useable_output() {
   printf "%s\n" "$*" >&2
}

leaprun_useable_test() {
   use_leaprun='no'

   ## privleap / leaprun is supposed to work fine even if called as root.
   ## Due to preference for failing early, hard and noisy, not giving special
   ## treatment for account 'root'.
#    local id_user
#    if ! id_user="$(id --user)" ; then
#       leaprun_useable_result="$0: WARNING: Cannot run 'id --user'. Cannot use privleap."
#       leaprun_useable_output "$leaprun_useable_result"
#       return 0
#    fi
#
#    if [ "$id_user" = "0" ] ; then
#       true "$0: INFO: Already using account root / id 0. No need to use privleap."
#       return 0
#    fi

   if ! leaprun_exe="$(command -v leaprun)"; then
      leaprun_useable_result="$0: WARNING: leaprun executable cannot be found. Cannot use privleap."
      leaprun_useable_output "$leaprun_useable_result"
      return 0
   fi

   if ! [ -f "/run/privleapd/pid" ]; then
      leaprun_useable_result="$0: WARNING: Cannot check if privleapd is not running. File '/run/privleapd/pid' does not exist. Cannot use privleap."
      leaprun_useable_output "$leaprun_useable_result"
      return 0
   fi

   if ! [ -r "/run/privleapd/pid" ]; then
      leaprun_useable_result="$0: WARNING: Cannot check if privleapd is not running. File '/run/privleapd/pid' is not readable. Cannot use privleap."
      leaprun_useable_output "$leaprun_useable_result"
      return 0
   fi

   local privleap_pid
   if ! privleap_pid="$(cat /run/privleapd/pid)"; then
      leaprun_useable_result="$0: WARNING: Failed to execute 'cat /run/privleapd/pid'. Cannot use privleap."
      leaprun_useable_output "$leaprun_useable_result"
      return 0
   fi

   if ! is_positive_integer "${privleap_pid}"; then
      leaprun_useable_result="$0: WARNING: privleapd pid file '/run/privleapd/pid' is empty or does not contain a number. Cannot use privleap."
      leaprun_useable_output "$leaprun_useable_result"
      return 0
   fi

   if ! [ -d "/proc/${privleap_pid}" ]; then
      leaprun_useable_result="$0: WARNING: privleapd is not running. Folder '/proc/${privleap_pid}' does not exist. Cannot use privleap."
      leaprun_useable_output "$leaprun_useable_result"
      return 0
   fi

   local my_user_id
   if ! my_user_id="$(id --user)"; then
      leaprun_useable_result="$0: WARNING: Failed to execute 'id --user'. Cannot use privleap."
      leaprun_useable_output "$leaprun_useable_result"
      return 0
   fi

   if ! [ -e "/run/privleapd/comm/${my_user_id}" ]; then
      leaprun_useable_result="$0: WARNING: Cannot communicate with privleapd. File '/run/privleapd/comm/${my_user_id}' does not exist. Cannot use privleap.

You might be able to create a privleap socket by executing: sudo leapctl --create '${USER:-${my_user_id}}'"
      leaprun_useable_output "$leaprun_useable_result"
      return 0
   fi

   use_leaprun='yes'
}

leaprun_useable_test
