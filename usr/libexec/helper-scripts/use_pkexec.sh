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

   if ! [[ "${kernel_cmdline}" =~ 'boot-role=sysmaint' ]]; then
      true "INFO: user mode boot detected. (Not sysmaint boot mode.)"
      true "INFO: (kernel parameter 'boot-role=sysmaint' is not present, ok.)"
   else
      true "INFO: sysmaint boot mode detected."
      true "INFO: (kernel parameter 'boot-role=sysmaint' present, ok.)"
   fi

   if ! test -x "$pkexec_exe"; then
      true "$0: INFO: pkexec is not executable. Cannot use pkexec."
      return 0
   fi

   use_pkexec='yes'
}

pkexec_useable_test
