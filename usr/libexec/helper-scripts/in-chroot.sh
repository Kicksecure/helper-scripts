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

in_chroot() {
  if ! mountpoint /proc >/dev/null 2>/dev/null; then
    ## If /proc is not mounted, we're almost certainly within a chroot.
    return 0
  fi

  ## Detection techniques inspired by
  ## https://unix.stackexchange.com/questions/14345/how-do-i-tell-im-running-in-a-chroot
  if [ "$(id -u)" = '0' ]; then
    if [ "$(stat / | tail -n+2)" != "$(stat /proc/1/root/. | tail -n+2)" ]; then
      return 0
    fi
  else
    local grep_cmd init_mountinfo self_mountinfo
    grep_cmd=( "grep" '[^ ]\+ [^ ]\+ [^ ]\+ [^ ]\+ / ' )
    init_mountinfo="$(cat /proc/1/mountinfo | "${grep_cmd[@]}")"
    self_mountinfo="$(cat "/proc/$$/mountinfo" | "${grep_cmd[@]}")"
    if [ "${init_mountinfo}" != "${self_mountinfo}" ]; then
      return 0
    fi
  fi

  return 1
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  in_chroot
fi
