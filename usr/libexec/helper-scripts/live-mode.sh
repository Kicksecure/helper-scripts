#!/bin/bash

## Copyright (C) 2012 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  set -o errexit
  set -o nounset
  set -o errtrace
  set -o pipefail
  proc_cmdline_output=$(cat -- /proc/cmdline)
else
  if [ -z "${proc_cmdline_output+x}" ]; then
    error "proc_cmdline_output is unset"
    return 1
    exit 1
  fi
fi

## Detect if the system was booted in live mode
## Check for 'rd.live.image' first, because both, ISO and grub-live come with 'boot=live' kernel parameter.
if printf "%s" "${proc_cmdline_output}" | grep --quiet --fixed-strings -e 'root=live' -e 'rd.live.image'; then
   live_status_detected_live_mode_environment_pretty="ISO Live"
   live_status_detected_live_mode_environment_machine="iso-live"
   live_status_word_pretty="ISO"
   live_status_detected="true"
   live_status_maybe_iso_live_message="<br/><u>This message can be safely ignored if only using this ISO to install to the hard drive.</u><br/>"
elif printf "%s" "${proc_cmdline_output}" | grep --quiet --fixed-strings -e 'boot=live' -e 'rootovl' -e 'rd.live.overlay.overlayfs=1' ; then
   live_status_detected_live_mode_environment_pretty="grub-live"
   live_status_detected_live_mode_environment_machine="grub-live"
   live_status_word_pretty="Live"
   live_status_detected="true"
   live_status_maybe_iso_live_message=""
else
   live_status_detected_live_mode_environment_pretty="false"
   live_status_detected_live_mode_environment_machine="false"
   live_status_word_pretty="persistent"
   live_status_detected="false"
   live_status_maybe_iso_live_message=""
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
