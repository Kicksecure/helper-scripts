#!/bin/bash

## Copyright (C) 2012 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  set -o errexit
  set -o nounset
  set -o errtrace
#  set -o pipefail
fi

was_pipefail_enabled='false'
if [ -o pipefail ]; then
  was_pipefail_enabled='true'
  set +o pipefail
fi

if [ -z "${proc_mount_contents+x}" ]; then
  proc_mount_contents="$(cat /proc/self/mounts)"
fi

live_state_str='live'
live_mode_str='none'

while read -r line; do
  IFS=' ' read -r -a line_parts <<< "${line}"
  if [ "${#line_parts[@]}" != '6' ]; then
    continue
  fi
  src_device="${line_parts[0]}"
  mount_point="${line_parts[1]}"
  fs_type="${line_parts[2]}"
  opt_str="${line_parts[3]}"
  if [[ "${src_device}" =~ ^/dev/ ]] \
    || [[ "${fs_type}" =~ ^(nfs|vboxsf|virtiofs|9pfs) ]]; then

    IFS=',' read -r -a opt_parts <<< "${opt_str}"
    rw_found='false'
    for opt_part in "${opt_parts[@]}"; do
      if [ "${opt_part}" = 'rw' ]; then
        rw_found='true'
        break
      fi
    done

    if [ "${rw_found}" = 'true' ]; then
      if [ "${live_state_str}" = 'live' ]; then
        live_state_str='semi-persistent-safe'
      fi

      if [ "${mount_point}" = '/' ]; then
        live_state_str='persistent'
        break
      elif ! [[ "${mount_point}" =~ ^/media/ ]] \
        && ! [[ "${mount_point}" =~ ^/mnt/ ]] \
        && ! [ "${mount_point}" = '/media' ] \
        && ! [ "${mount_point}" = '/mnt' ]; then
        live_state_str='semi-persistent-unsafe'
      elif [ "$(printf '%s' "${src_device}" | sed 's/[^\/]//g' | wc -c)" = 2 ] \
        && ! [ -f "/sys/class/block/${src_device##*/}/removable" ]; then
        live_state_str='semi-persistent-unsafe'
      fi
    fi
  fi
done <<< "${proc_mount_contents}"

if [ "${live_state_str}" != 'persistent' ]; then
  while read -r line; do
    if [[ "${line}" =~ ^LiveOS_rootfs\ / ]]; then
      if [ "${live_state_str}" = 'live' ]; then
        live_mode_str='iso-live'
      else
        live_mode_str='iso-live-semi-persistent'
      fi
    fi
  done <<< "${proc_mount_contents}"

  if [ "${live_mode_str}" = 'none' ]; then
    if [ "${live_state_str}" = 'live' ]; then
      live_mode_str='grub-live'
    else
      live_mode_str='grub-live-semi-persistent'
    fi
  fi

  if [ "${live_mode_str}" = 'iso-live' ] && [ "${live_state_str}" = 'live' ]; then
    live_status_detected_live_mode_environment_pretty="ISO Live"
    live_status_detected_live_mode_environment_machine="iso-live"
    live_status_word_pretty="ISO"
    live_status_detected="true"
    live_status_maybe_iso_live_message="<br/><u>This message can be safely ignored if only using this ISO to install to the hard drive.</u><br/>"
  elif [ "${live_mode_str}" = 'iso-live-semi-persistent' ] && [ "${live_state_str}" = 'semi-persistent-safe' ]; then
    live_status_detected_live_mode_environment_pretty="ISO Live (semi-persistent)"
    live_status_detected_live_mode_environment_machine="iso-live-semi-persistent"
    live_status_word_pretty="ISO"
    live_status_detected="true"
    live_status_maybe_iso_live_message="<br/><u>This message can be safely ignored if only using this ISO to install to the hard drive.</u><br/>"
  elif [ "${live_mode_str}" = 'iso-live-semi-persistent' ] && [ "${live_state_str}" = 'semi-persistent-unsafe' ]; then
    live_status_detected_live_mode_environment_pretty="ISO Live (semi-persistent)"
    live_status_detected_live_mode_environment_machine="iso-live-semi-persistent-unsafe"
    live_status_word_pretty="ISO"
    live_status_detected="true"
    live_status_maybe_iso_live_message="<br/><u>This message can be safely ignored if only using this ISO to install to the hard drive.</u><br/>"
  elif [ "${live_mode_str}" = 'grub-live' ] && [ "${live_state_str}" = 'live' ]; then
    live_status_detected_live_mode_environment_pretty="grub-live"
    live_status_detected_live_mode_environment_machine="grub-live"
    live_status_word_pretty="Live"
    live_status_detected="true"
    live_status_maybe_iso_live_message=""
  elif [ "${live_state_str}" = 'semi-persistent-safe' ]; then
    live_status_detected_live_mode_environment_pretty="grub-live-semi-persistent"
    live_status_detected_live_mode_environment_machine="grub-live-semi-persistent"
    live_status_word_pretty="Semi-persistent"
    live_status_detected="true"
    live_status_maybe_iso_live_message=""
  elif [ "${live_state_str}" = 'semi-persistent-unsafe' ]; then
    live_status_detected_live_mode_environment_pretty="grub-live-semi-persistent"
    live_status_detected_live_mode_environment_machine="grub-live-semi-persistent-unsafe"
    live_status_word_pretty="Semi-persistent"
    live_status_detected="true"
    live_status_maybe_iso_live_message=""
  fi
else
  live_status_detected_live_mode_environment_pretty="false"
  live_status_detected_live_mode_environment_machine="false"
  live_status_word_pretty="persistent"
  live_status_detected="false"
  live_status_maybe_iso_live_message=""
fi

if [ "$was_pipefail_enabled" = 'true' ]; then
  set -o pipefail
fi

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  var_list=(
    "live_status_detected_live_mode_environment_pretty"
    "live_status_detected_live_mode_environment_machine"
    "live_status_word_pretty"
    "live_status_detected"
    "live_status_maybe_iso_live_message"
  )

  ## Print out in format suitable for 'eval' and 'grep'.
  for var_name in "${var_list[@]}"; do
    ## Single quotes. Do not change without reflecting this change by users of this script.
    printf "%s='%s'\n" "$var_name" "${!var_name}"
  done
fi
