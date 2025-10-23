#!/bin/bash

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

pkexec_useable_test() {
   local kernel_cmdline

   use_pkexec='no'

   if ! pkexec_exe="$(command -v pkexec)"; then
      true "$0: INFO: pkexec executable cannot be found. Cannot use pkexec."
      return 0
   fi

   kernel_cmdline="$(cat -- /proc/cmdline)"

   ## Debugging.
   ## sets: boot_session
   source /usr/libexec/helper-scripts/boot-session-detection.sh

   if ! test -x "$pkexec_exe"; then
      true "$0: INFO: pkexec is not executable. Cannot use pkexec."
      return 0
   fi

   use_pkexec='yes'
}

pkexec_useable_test
