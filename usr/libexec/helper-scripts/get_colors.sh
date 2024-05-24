#!/bin/bash

## colors
# shellcheck disable=SC2034
get_colors(){
  get_colors_sourced=1
  ## Disable colors if some environment variables are present.
  if test -n "${NO_COLOR:-}" || test -n "${ANSI_COLORS_DISABLED:-}"; then
    nocolor=""
    bold=""
    nobold=""
    underline=""
    nounderline=""
    red=""
    green=""
    yellow=""
    blue=""
    magenta=""
    cyan=""
    return 0
  fi

  nocolor="\033[0m"
  bold="\033[1m"
  nobold="\033[22m"
  underline="\033[4m"
  nounderline="\033[24m"
  red="\033[31m"
  green="\033[32m"
  yellow="\033[33m"
  blue="\033[34m"
  magenta="\033[35m"
  cyan="\033[36m"
}

if test "${get_colors_sourced:-}" != "1"; then
  get_colors
fi
