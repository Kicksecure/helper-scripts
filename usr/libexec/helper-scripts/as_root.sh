#!/bin/bash

source /usr/libexec/helper-scripts/get_colors.sh
source /usr/libexec/helper-scripts/log_run_die.sh

## Block not running as root.
as_root(){
  if test "$(id -u)" != "0"; then
    die 1 "\
${underline}Root Check:${nounderline} Not running as root.
  - You are currently running this script without root privileges.
  - This script should be run as root."
  fi
}
