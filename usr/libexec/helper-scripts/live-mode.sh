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

if [ -z "${mount_command_output+x}" ]; then
  mount_command_output="$(mount)"
fi

## Detect if the system was booted in live mode
## Check for 'rd.live.image' first, because both, ISO and grub-live come with 'boot=live' kernel parameter.
if printf "%s" "${mount_command_output}" 2>/dev/null | grep 'LiveOS_rootfs on / type overlay' &>/dev/null; then
  live_status_detected_live_mode_environment_pretty="ISO Live"
  live_status_detected_live_mode_environment_machine="iso-live"
  live_status_word_pretty="ISO"
  live_status_detected="true"
  live_status_maybe_iso_live_message="<br/><u>This message can be safely ignored if only using this ISO to install to the hard drive.</u><br/>"
elif printf "%s" "${mount_command_output}" 2>/dev/null | grep 'overlay on / type overlay' &>/dev/null; then
  if printf "%s" "${mount_command_output}" 2>/dev/null | grep '/dev/.* on /home ' &>/dev/null; then
    live_status_detected_live_mode_environment_pretty="grub-live-semi-persistent"
    live_status_detected_live_mode_environment_machine="grub-live-semi-persistent"
    live_status_word_pretty="Semi-persistent"
    live_status_detected="true"
    live_status_maybe_iso_live_message=""
  else
    live_status_detected_live_mode_environment_pretty="grub-live"
    live_status_detected_live_mode_environment_machine="grub-live"
    live_status_word_pretty="Live"
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
