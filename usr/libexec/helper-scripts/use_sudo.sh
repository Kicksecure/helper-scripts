#!/bin/bash

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

sudo_useable_test() {
   use_sudo='no'

#    local id_user
#    if ! id_user="$(id --user)" ; then
#       echo "$0: WARNING: Cannot run 'id --user'. Cannot use sudo." >&2
#       return 0
#    fi
#
#    if [ "$id_user" = "0" ] ; then
#       true "$0: INFO: Already using account root / id 0. No need to use sudo."
#       return 0
#    fi

   if ! sudo_exe="$(command -v sudo)"; then
      true "$0: INFO: sudo executable cannot be found. Cannot use sudo."
      return 0
   fi

   ## Debugging.
   ## sets: boot_session
   source /usr/libexec/helper-scripts/boot-session-detection.sh

   if ! test -x "$sudo_exe"; then
      true "$0: INFO: sudo is not executable. Cannot use sudo."
      return 0
   fi

   use_sudo='yes'
}

sudo_error_exit_if_unavailable() {
   if [ "$use_sudo" = "no" ]; then
      printf '%s\n' "ERROR: sudo unavailable. Boot into sysmaint session?"
      exit 1
   fi
}

sudo_useable_test
