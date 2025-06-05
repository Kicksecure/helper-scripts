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

writable_fs_lists_str="$(/usr/libexec/helper-scripts/get_writable_fs_lists.sh)"
readarray -t writable_fs_lists <<< "${writable_fs_lists_str}"
IFS=' ' read -r -a safe_writable_fs_list <<< "${writable_fs_lists[0]:-}"
IFS=' ' read -r -a danger_writable_fs_list <<< "${writable_fs_lists[1]:-}"
if [ "${#safe_writable_fs_list[@]}" = '0' ] \
  || [ -z "${safe_writable_fs_list[0]}" ]; then
  safe_writable_list_empty='true'
else
  safe_writable_list_empty='false'
fi
if [ "${#danger_writable_fs_list[@]}" = '0' ] \
  || [ -z "${danger_writable_fs_list[0]}" ]; then
  danger_writable_list_empty='true'
else
  danger_writable_list_empty='false'
fi
for danger_writable_fs in "${danger_writable_fs_list[@]}"; do
  if [ "${danger_writable_fs}" = '/' ]; then
    live_state_str='persistent'
    break
  fi
done
if [ "${live_state_str}" = 'live' ] \
  && [ "${danger_writable_list_empty}" = 'false' ]; then
  live_state_str='semi-persistent-unsafe'
elif [ "${live_state_str}" = 'live' ] \
  && [ "${safe_writable_list_empty}" = 'false' ]; then
  live_state_str='semi-persistent-safe'
fi

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
