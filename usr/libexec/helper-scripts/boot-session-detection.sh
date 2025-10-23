#!/bin/bash

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

boot_session_detection() {
  local kernel_cmdline

  kernel_cmdline="$(cat -- /proc/cmdline)"

  if ! [[ "${kernel_cmdline}" =~ 'boot-role=sysmaint' ]]; then
    true "INFO: USER Session detected."
    true "INFO: (kernel parameter 'boot-role=sysmaint' is not present, ok.)"
    boot_session="user_session"
  else
    true "INFO: SYSMAINT Session detected."
    true "INFO: (kernel parameter 'boot-role=sysmaint' present, ok.)"
    boot_session="sysmaint_session"
  fi
}

boot_session_detection
