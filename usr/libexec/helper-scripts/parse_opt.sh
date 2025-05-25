#!/bin/bash

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

source /usr/libexec/helper-scripts/ip_syntax.sh
source /usr/libexec/helper-scripts/log_run_die.sh

## ------------------- ##
## Usage of parse_opt.sh
##
##  usage(){
##    printf '%s\n' "Usage: ${0##*/} [OPTIONS]
##    -o, --opt-wo-arg       option without argument
##    -w, --opt-with-arg     option with argument
##    "
##    exit "${1}"
##  }
##
##  opt_wo_arg=""
##  opt_with_arg=""
##
##  while true; do
##    begin_optparse "${1:-}" "${2:-}" || break
##    case "${opt}" in
##      o|opt-wo-arg) opt_wo_arg=1;;
##      w|opt-with-arg) get_arg; opt_with_arg="${arg}";;
##      h|help) usage 0;;
##      "") break;;
##      *) die 2 "Invalid option: '${opt_orig}'"
##    esac
##    shift "${shift_n:-1}"
##  done
##
##  range_arg opt_with_arg "${opt_with_arg}" p1 p2
##
##  log info "opt_wo_arg=$opt_wo_arg"
##  log info "opt_with_arg=$opt_with_arg"
## ------------------- ##


## Begin parsing options.
## function should be called before the case statement to assign the options
## to a temporary variable
## Usage: begin_optparse "${1:-}" "${2:-}" || break
begin_optparse(){
  ## options ended
  test -z "${1:-}" && return 1
  shift_n=""
  ## save opt orig for error message to understand which opt failed
  opt_orig="${1}"
  # shellcheck disable=SC2034
  ## need to pass the second positional parameter cause maybe it is an argument
  arg_possible="${2}"
  clean_opt "${1}" || return 1
}


## Clean options.
## '--option=value' should shift once and '--option value' should shift twice
## but at this point it is not possible to be sure if option requires an
## argument, reset shift to zero, at the end, if it is still 0, it will be
## assigned to one, has to be zero here so we can check later if option
## argument is separated by space ' ' or equal sign '='
clean_opt(){
  case "${opt_orig}" in
    "")
      ## options ended
      return 1
      ;;
    --)
      ## stop option parsing
      shift 1
      return 1
      ;;
    --*=*)
      ## long option '--sleep=1'
      opt="${opt_orig%=*}"
      opt="${opt#*--}"
      arg="${opt_orig#*=}"
      shift_n=1
      ;;
    -*=*)
      ## short option '-s=1'
      opt="${opt_orig%=*}"
      opt="${opt#*-}"
      arg="${opt_orig#*=}"
      shift_n=1
      ;;
    --*)
      ## long option '--sleep 1'
      opt="${opt_orig#*--}"
      arg="${arg_possible}"
      ;;
    -*)
      ## short option '-s 1'
      opt="${opt_orig#*-}"
      arg="${arg_possible}"
      ;;
    *)
      ## not an option
      usage 2
      ;;
  esac
}


get_arg(){
  ## if argument is empty or starts with '-', fail as it possibly is an option
  case "${arg:-}" in
    ""|-*)
      die 2 "Option '${opt_orig}' requires an argument."
      ;;
  esac

  ## shift positional argument two times, as this option demands argument,
  ## unless they are separated by equal sign '='
  ## shift_n default value was assigned when trimming dashes '--' from the
  ## options. If shift_n is equal to zero, '--option arg', if shift_n is not
  ## equal to zero, '--option=arg'
  if test -z "${shift_n}"; then
    shift_n=2
  fi
}

## Check if argument is within range
## usage:
## $ range_arg key "${key}" "1" "2" "3" "4" "5"
## $ range_arg key "${key}" "a" "b" "c" "A" "B" "C"
range_arg(){
  key="${1}"
  var="${2}"
  shift 2
  list="${*:-}"
  #range="${list#"${1} "}"
  if [ -n "${var:-}" ]; then
    success=0
    for tests in ${list:-}; do
      ## only evaluate if matches all chars
      [ "${var:-}" = "${tests}" ] && success=1 && break
    done
    ## if not within range, fail and show the fixed range that can be used
    if [ ${success} -eq 0 ]; then
      die 2 "Option '${key}' cannot be '${var:-}'. Possible values: '${list}'"
    fi
  fi
}
