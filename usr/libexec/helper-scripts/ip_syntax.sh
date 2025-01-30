#!/bin/bash

source /usr/libexec/helper-scripts/get_colors.sh
source /usr/libexec/helper-scripts/log_run_die.sh

## Check if variable is integer
is_integer(){
  printf %d "${1}" >/dev/null 2>&1 || return 1
}


## Checks if the target is valid.
## Address range from 0.0.0.0 to 255.255.255.255. Port ranges from 0 to 65535
## this is not perfect but it is better than nothing
is_addr_port(){
  addr_port="${1}"
  port="${addr_port##*:}"
  addr="${addr_port%%:*}"

  ## Support only IPv4 x.x.x.x:y
  # shellcheck disable=SC2154
  if [ "$(printf '%s' "${addr_port}" | tr -cd "." | wc -c)" != 3 ] ||
    [ "$(printf '%s' "${addr_port}" | tr -cd ":" | wc -c)" != 1 ] ||
    [ "${port}" = "${addr}" ]
  then
    die 2 "${underline}is_addr_port test:${nounderline} Invalid address:port assignment: ${addr_port}"
  fi

  is_integer "${port}" ||
    die 2 "${underline}is_addr_port test:${nounderline} Invalid port '${port}', not an integer."

  if [ "${port}" -gt 0 ] && [ "${port}" -le 65535 ]; then
    true "is_addr_port test: Valid port: '${port}'"
  else
    die 2 "${underline}is_addr_port test:${nounderline} Invalid port '${port}', not within range: 0-65535."
  fi

  for quad in $(printf '%s\n' "${addr}" | tr "." " "); do
    is_integer "${quad}" ||
      die 2 "${underline}is_addr_port test:${nounderline} Invalid address '${addr}', '${quad}' is not an integer."
    if [ "${quad}" -ge 0 ] && [ "${quad}" -le 255 ]; then
      true "Valid quad '${quad}'"
    else
      die 2 "${underline}is_addr_port test:${nounderline} Invalid address '${addr}', '${quad}' not within range: 0-255."
    fi
  done
}
