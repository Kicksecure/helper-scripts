#!/bin/bash

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## Not possible because 'dist-installer-cli' includes this script verbatim in full.
# if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
#   true "$0: START"
#   set -o errexit
#   set -o nounset
#   set -o errtrace
#   set -o pipefail
# fi

# shellcheck disable=SC2034
get_colors() {
  get_colors_sourced=1

  if test -n "${NO_COLOR:-}" || test -n "${ANSI_COLORS_DISABLED:-}" || \
    test -z "${TERM:-}" || test "${TERM:-}" = "dumb" || test "${TERM:-}" = "unknown" || \
    ! test -t 2; then
      nocolor=""; reset=""
      bold=""; nobold=""
      underline=""; nounderline=""
      under=""; eunder=""
      stout=""; estout=""
      blink=""
      italic=""; eitalic=""
      red=""; green=""; yellow=""; blue=""; magenta=""; cyan=""; white=""
      default=""
      alt=""; ealt=""
      hide=""; show=""
      save=""; load=""
      eed=""; eel=""; ebl=""; ewl=""
      back=""
      draw="" ## Intentionally not implemented, see below
    return 0
  fi

  ## Use printf -v so xtrace shows "\033" text, not raw escape bytes.
  printf -v nocolor     '%b' "\033[0m"
  ## Effects in xtrace.
  #reset="${nocolor}"
  printf -v reset       '%b' "\033[0m"

  printf -v bold        '%b' "\033[1m"
  printf -v nobold      '%b' "\033[22m"

  printf -v underline   '%b' "\033[4m"
  printf -v nounderline '%b' "\033[24m"
  ## Effects in xtrace.
  #under="${underline}"
  #eunder="${nounderline}"
  printf -v under       '%b' "\033[4m"
  printf -v eunder      '%b' "\033[24m"

  printf -v stout       '%b' "\033[7m"
  printf -v estout      '%b' "\033[27m"

  printf -v blink       '%b' "\033[5m"

  printf -v italic      '%b' "\033[3m"
  printf -v eitalic     '%b' "\033[23m"

  printf -v red         '%b' "\033[31m"
  printf -v green       '%b' "\033[32m"
  printf -v yellow      '%b' "\033[33m"
  printf -v blue        '%b' "\033[34m"
  printf -v magenta     '%b' "\033[35m"
  printf -v cyan        '%b' "\033[36m"
  printf -v white       '%b' "\033[37m"
  printf -v default     '%b' "\033[39m"

  printf -v alt         '%b' "\033[?1049h"
  printf -v ealt        '%b' "\033[?1049l"

  printf -v hide        '%b' "\033[?25l"
  printf -v show        '%b' "\033[?25h"

  printf -v save        '%b' "\0337"
  printf -v load        '%b' "\0338"

  printf -v eed         '%b' "\033[J"   # erase to end of display
  printf -v eel         '%b' "\033[K"   # erase to end of line
  printf -v ebl         '%b' "\033[1K"  # erase to beginning of line
  printf -v ewl         '%b' "\033[2K"  # erase whole line

  printf -v back        '%b' "\b"
}

get_colors_test() {
  ## This function is only meant for manual visual verification.
  ## It prints one feature per line, resetting after each line so styles
  ## does not leak into the next output.

  printf '%s\n' "$0: test mode"

  ## Ensure variables are initialized (in case someone calls test directly).
  ## Not needed because when 'source'ing this script, it's already load.
  #get_colors

  ## --- Colors -------------------------------------------------------
  ## Foreground colors (8-color ANSI). Each line prints the color name in that color.
  printf '%b\n' "${red}red${nocolor}"
  printf '%b\n' "${green}green${nocolor}"
  printf '%b\n' "${yellow}yellow${nocolor}"
  printf '%b\n' "${blue}blue${nocolor}"
  printf '%b\n' "${magenta}magenta${nocolor}"
  printf '%b\n' "${cyan}cyan${nocolor}"
  printf '%b\n' "${white}white${nocolor}"

  ## Reset to terminal default foreground color (may differ from white).
  printf '%b\n' "${default}default${nocolor}"

  ## --- Text attributes ----------------------------------------------
  ## Bold / increased intensity.
  printf '%b\n' "${bold}bold${nocolor}"

  ## Cancel bold / intensity (may not affect underline/italic).
  printf '%b\n' "${nobold}nobold${nocolor}"

  ## Italic (may be unsupported or rendered as reverse/underline on some terminals).
  printf '%b\n' "${italic}italic${nocolor}"

  ## Cancel italic (not tested by default; usually harmless).
  #printf '%b\n' "${eitalic}eitalic${nocolor}"

  ## Underline.
  printf '%b\n' "${underline}underline${nocolor}"

  ## Cancel underline (not tested by default; usually harmless).
  #printf '%b\n' "${nounderline}nounderline${nocolor}"

  ## Standout / reverse video (often swaps foreground/background).
  printf '%b\n' "${stout}stout${nocolor}"

  ## Cancel standout / reverse video.
  printf '%b\n' "${estout}estout${nocolor}"

  ## Blinking text.
  printf '%b\n' "${blink}blink${nocolor}"

  ## --- Cursor / screen control --------------------------------------
  ## Hide cursor, print "hide", then show cursor again.
  ## Useful to confirm the escape sequences do not break output.
  printf '%b\n' "${hide}hide${show}${nocolor}"

  ## Cursor save/restore (not tested by default because it can look odd
  ## depending on where the cursor is when printed).
  #printf '%b\n' "${save}save${load}${nocolor}"

  ## Erase to end of display (J) / end of line (K) / beginning of line (1K)
  ## / whole line (2K). These are hard to "see" in a simple print, but
  ## included for completeness.
  #printf '%b\n' "${eed}eed${nocolor}"
  #printf '%b\n' "${eel}eel${nocolor}"
  #printf '%b\n' "${ebl}ebl${nocolor}"
  #printf '%b\n' "${ewl}ewl${nocolor}"

  ## Backspace character. Typically moves cursor one column left; visual
  ## effect depends on surrounding output.
  #printf '%b\n' "${back}back${nocolor}"

  ## Drawing characters capability is intentionally unsupported in this
  ## modern implementation; kept for compatibility (usually empty).
  printf '%s\n' "draw: ${draw:-}"
}

if test "${get_colors_sourced:-}" != "1"; then
  get_colors
fi

# if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
#   get_colors_test
#   true "$0: END"
# fi
