#!/bin/bash

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  set -o xtrace
  set -o errexit
  set -o nounset
  set -o errtrace
  set -o pipefail
fi

command -v mountpoint >/dev/null
command -v id >/dev/null
command -v grep >/dev/null
command -v cat >/dev/null

in_chroot_extra() {
  if ! mountpoint -- /proc >/dev/null 2>/dev/null; then
    true "INFO: /proc is not mounted, we're almost certainly within a chroot, therefore 'return 0'."
    return 0
  fi

  ## Detection techniques inspired by
  ## https://unix.stackexchange.com/questions/14345/how-do-i-tell-im-running-in-a-chroot
  if [ "$(id -u)" = '0' ]; then
    true "INFO: running as root: yes"
    if [ "$(stat / | tail -n+2)" != "$(stat -- /proc/1/root/. | tail -n+2)" ]; then
      true "INFO: /proc/1/root based detection found chroot, therefore 'return 0'."
      return 0
    fi
  else
    true "INFO: running as root: no"
    local grep_cmd init_mountinfo self_mountinfo
    grep_cmd=( "grep" '[^ ]\+ [^ ]\+ [^ ]\+ [^ ]\+ / ' )
    init_mountinfo="$(cat -- "/proc/1/mountinfo" | "${grep_cmd[@]}")"
    self_mountinfo="$(cat -- "/proc/$$/mountinfo" | "${grep_cmd[@]}")"
    if [ "${init_mountinfo}" != "${self_mountinfo}" ]; then
      true "INFO: /proc/1/mountinfo based detection found chroot, therefore 'return 0'."
      return 0
    fi
  fi

  true "INFO: Not a chroot. Therefore 'return 1'."
  return 1
}

in_chroot() {
  if ischroot --default-false; then
    true "INFO: ischroot determined we are inside a chroot."
    ## Use 'in_chroot_extra' to confirm.

    ## TODO: Needed?
    in_chroot_extra
    ## TODO: Can we simply 'return 0' here or should we rely on the
    ##       exit code determined by 'in_chroot_extra'?
    #return 0
  else
    true "INFO: ischroot determined we are NOT inside a chroot, therefore 'return 1'."
    return 1
  fi
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  in_chroot
fi
