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

  printf -v nocolor     '%b' "\033[0m"
  printf -v bold        '%b' "\033[1m"
  printf -v nobold      '%b' "\033[22m"
  printf -v underline   '%b' "\033[4m"
  printf -v nounderline '%b' "\033[24m"
  printf -v red         '%b' "\033[31m"
  printf -v green       '%b' "\033[32m"
  printf -v yellow      '%b' "\033[33m"
  printf -v blue        '%b' "\033[34m"
  printf -v magenta     '%b' "\033[35m"
  printf -v cyan        '%b' "\033[36m"
}

if test "${get_colors_sourced:-}" != "1"; then
  get_colors
fi
