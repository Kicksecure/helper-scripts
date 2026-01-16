#!/bin/bash

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

source /usr/libexec/helper-scripts/get_colors.sh

if ! command -v stecho &>/dev/null ; then
  ## Fallback to 'printf' in case 'stecho' is unavailable.
  stecho() {
    printf "%s\n" "$*"
  }
fi

disable_xtrace() {
  if test "${xtrace:-}" = "1"; then
    xtrace_was_on=true
    set +o xtrace
  else
    xtrace_was_on=false
  fi
}

xtrace_reenable_maybe() {
  trap '' RETURN
  if [ "${xtrace_was_on:-}" = "true" ]; then
    set -o xtrace
  fi
}

__log_level_num() {
  case "${1:-notice}" in
    bug|error) printf '%s' 0 ;;
    question)  printf '%s' 0 ;;
    warn)      printf '%s' 1 ;;
    notice)    printf '%s' 2 ;;
    info)      printf '%s' 3 ;;
    debug)     printf '%s' 4 ;;
    echo)      printf '%s' 5 ;;
    null)      printf '%s' 6 ;;
    *)         printf '%s' 2 ;; ## unknown -> treat as notice
  esac
  return 0
}

## Logging mechanism with easy customization of message format as well as
## standardization on how the messages are delivered.
## usage: log_type message
## usage: log [info|notice|warn|error|debug|bug|echo|null] "X occurred."
## Variable to define by calling script (caller_level_num): log_level
log() {
  local log_level="${log_level:-notice}"

  ## Avoid clogging output if log() is working alright.
  disable_xtrace
  trap 'xtrace_reenable_maybe' RETURN

  local log_type log_type_up log_color log_source_script log_level_colorized log_content log_full
  local should_print=0
  local caller_level_num msg_level_num

  log_type="${1:-notice}"

  if (( $# > 0 )); then
    shift || true
  fi

  ## capitalize log level
  log_type_up="${log_type^^}"

  ## set formatting based on log level
  case "${log_type}" in
    bug)
      log_color="${yellow}"
      ;;
    question)
      log_color="${blue}"
      ;;
    error)
      log_color="${red}"
      ;;
    warn)
      log_color="${magenta}"
      ;;
    info)
      log_color="${cyan}"
      ;;
    debug)
      log_color="${cyan}"
      ;;
    notice)
      log_color="${green}"
      ;;
    echo)
      log_color=""
      ;;
    null)
      log_color=""
      ;;
    *)
      ## Avoid recursion into log() on unsupported type; print directly.
      #log bug "Unsupported log type specified: '${log_type}'"
      stecho "${0##*/}: [${red}BUG${nocolor}]: Unsupported log type specified: '${log_type}'" >&2
      die 1 "Please report this bug."
      return 0
      ;;
  esac
  ## uniform log format
  log_color="${bold}${log_color}"
  log_source_script="${0##*/}"
  if [ -n "${who_ami-}" ]; then
    log_who_ami_maybe="(${who_ami-}) "
  fi
  log_level_colorized="[${log_color}${log_type_up}${nocolor}]"
  log_content="${*}"
  ## error logs are the minimum and should always be printed, even if
  ## failing to assign a correct log type
  ## send bugs and error to stdout and stderr
  log_full="${log_source_script} ${log_who_ami_maybe-}${log_level_colorized}: ${log_content}"
  case "${log_type}" in
    bug|error)
      stecho "${log_full}" >&2
      return 0
      ;;
    null)
      return 0
      ;;
  esac

  true "${FUNCNAME[0]}: INFO: log_level: $log_level | log_type: $log_type"
  caller_level_num="$(__log_level_num "${log_level}")"
  true "${FUNCNAME[0]}: INFO: log_level: $log_level | caller_level_num: $caller_level_num"
  msg_level_num="$(__log_level_num "${log_type}")"
  true "${FUNCNAME[0]}: INFO: log_type: $log_type | msg_level_num: $msg_level_num"

  if (( msg_level_num <= caller_level_num )); then
    should_print=1
  fi

  if [ "$should_print" = 1 ]; then
    stecho "${log_full}" >&2
  fi

  return 0
}


## For one liners 'log error; die'
## 'log' should not handle exits, because then it would not be possible
## to log consecutive errors on multiple lines, making die more suitable
## usage: die # "msg"
## where '#' is the exit code.
die() {
  log error "${2}"
  if test "${allow_errors:-}" = "1"; then
    log warn "Skipping termination because of with code '${1}' due to 'allow_errors' setting."
    return 0
  fi
  case "${1}" in
    106|107)
      true
      ;;
    *)
      log error "Aborting."
      ;;
  esac
  exit "${1}"
}


## Wrapper to log command before running to avoid duplication of code
log_run() {
  local level command_without_extraneous_spaces_temp command_without_extraneous_spaces
  level="${1}"
  shift || true

  printf -v command_without_extraneous_spaces_temp '%q ' "${@}"
  command_without_extraneous_spaces="$(printf "%s\n" "${command_without_extraneous_spaces_temp}")"
  if test "${dry_run:-}" = "1"; then
    log "${level}" "Skipping command (dry-run): $ ${command_without_extraneous_spaces}"
    return 0
  fi

  ## TODO: Still an issue? CI expects no output from root_cmd() which calls log_run().

  if test "${run_background:-}" = "1"; then
    log "${level}" "Background command starting: $ ${command_without_extraneous_spaces} &"
    "${@}" &
    background_pid="$!"
    disown "${background_pid}" || true
  else
    log "${level}" "Command executing: $ ${command_without_extraneous_spaces}"
    "${@}" || return 1
  fi
}


## Useful to get runtime mid run to log easily
## Variable to define outside: start_time
# shellcheck disable=SC2154
get_elapsed_time() {
  printf '%s\n' "$(($(date +%s) - start_time))"
}


## Log elapsed time, the name explains itself.
log_time() {
  log info "Time elapsed: $(get_elapsed_time)s."
}
