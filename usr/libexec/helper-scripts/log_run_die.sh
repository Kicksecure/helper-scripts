#!/bin/bash

source /usr/libexec/helper-scripts/get_colors.sh

## Logging mechanism with easy customization of message format as well as
## standardization on how the messages are delivered.
## usage: log [info|notice|warn|error] "X occurred."
## Variable to define outside: log_level
log(){
  ## Avoid clogging output if log() is working alright.
  if test "${xtrace:-}" = "1"; then
    set +o xtrace
  else
    case "${-}" in
      *x*)
        xtrace=1
        set +o xtrace
        ;;
    esac
  fi
  log_type="${1:-notice}"
  ## capitalize log level
  log_type_up="$(printf '%s' "${log_type}" | tr "[:lower:]" "[:upper:]")"
  shift 1
  ## set formatting based on log level
  case "${log_type}" in
    bug)
      log_color="${yellow}"
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
    notice)
      log_color="${green}"
      ;;
    null)
      log_color=""
      true
      ;;
    *)
      log bug "Unsupported log type specified: '${log_type}'"
      die 1 "Please report this bug."
  esac
  ## uniform log format
  log_color="${bold}${log_color}"
  log_source_script="${0##*/}: "
  log_level_colorized="[${log_color}${log_type_up}${nocolor}]: "
  log_content="${*}"
  ## error logs are the minimum and should always be printed, even if
  ## failing to assign a correct log type
  ## send bugs and error to stdout and stderr
  log_full="${log_source_script}${log_level_colorized}${log_content}"$'\n'
  case "${log_type}" in
    bug|error)
      stprint "${log_full}" >&2
      return 0
      ;;
    null)
      true
      ;;
  esac
  ## reverse importance order is required, excluding 'error'
  all_log_levels="warn notice info debug null"
  # shellcheck disable=SC2154
  if printf '%s' " ${all_log_levels} " | grep -o ".* ${log_level} " \
    | grep -q " ${log_type}"
  then
    case "${log_type}" in
      null)
        true
        ;;
      *)
        stprint "${log_full}" >&2
        ;;
    esac
  fi

  if test "${xtrace:-}" = "1"; then
    set -o xtrace
  fi
}


## For one liners 'log error; die'
## 'log' should not handle exits, because then it would not be possible
## to log consecutive errors on multiple lines, making die more suitable
## usage: die # "msg"
## where '#' is the exit code.
die(){
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
      log error "Installer aborting."
      ;;
  esac
  exit "${1}"
}


## Wrapper to log command before running to avoid duplication of code
log_run(){
  level="${1}"
  shift
  ## Extra spaces appearing when breaking log_run on multiple lines.
  command_without_extrarenous_spaces="$(printf '%s' "${@}" | tr -s " ")"
  if test "${dry_run:-}" = "1"; then
    log "${level}" "Skipping command: $ ${command_without_extrarenous_spaces}"
    return 0
  fi

  ## TODO: Still an issue? CI expects no output from root_cmd() which calls log_run().

  if test "${run_background:-}" = "1"; then
    log "${level}" "Background command starting: $ ${command_without_extrarenous_spaces} &"
    "${@}" &
    background_pid="$!"
    disown "$background_pid"
  else
    log "${level}" "Command executing: $ ${command_without_extrarenous_spaces}"
    "${@}" || return 1
  fi
}


## Useful to get runtime mid run to log easily
## Variable to define outside: start_time
# shellcheck disable=SC2154
get_elapsed_time(){
  printf '%s\n' "$(($(date +%s) - start_time))"
}


## Log elapsed time, the name explains itself.
log_time(){
  log info "Time elapsed: $(get_elapsed_time)s."
}
