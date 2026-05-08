#!/bin/bash

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

# shellcheck source=/usr/libexec/helper-scripts/get_colors.sh
source "${HELPER_SCRIPTS_PATH:-}"/usr/libexec/helper-scripts/get_colors.sh
# shellcheck source=/usr/libexec/helper-scripts/strings.bsh
source "${HELPER_SCRIPTS_PATH:-}"/usr/libexec/helper-scripts/strings.bsh
# shellcheck source=/usr/libexec/helper-scripts/xtrace.bsh
source "${HELPER_SCRIPTS_PATH:-}"/usr/libexec/helper-scripts/xtrace.bsh
# shellcheck source=/usr/libexec/helper-scripts/has.sh
source "${HELPER_SCRIPTS_PATH:-}"/usr/libexec/helper-scripts/has.sh

## Hard tool-availability check.
##
## log() and the BUG path inside it call out to two external
## commands:
##
##   stecho          - stdisplay package; renders log lines safely
##                     to stderr (control-character / ANSI-escape
##                     filtering).
##   sanitize-string - helper-scripts package; truncates and
##                     sanitizes log content before display.
##
## Earlier versions of this file silently stubbed 'stecho' to a
## plain printf when missing. That paper-over swallowed install
## misconfiguration bugs - a script would log fine in dev and
## explode mid-run on a stripped-down install. Stubbing has been
## removed; instead, detect the missing tool at source-time and
## bail with a pointer at the script that sourced us, so the
## fault site is obvious without grep-diving.
##
## Bootstrap order: this check runs AFTER has.sh is sourced (so
## 'has' is available) and BEFORE any log()/die() definition is
## relied on by callers (so the failure happens during 'source'
## rather than at first log call).
__log_run_die_missing=()
for __log_run_die_cmd in stecho sanitize-string; do
  has "${__log_run_die_cmd}" || __log_run_die_missing+=("${__log_run_die_cmd}")
done
if [ "${#__log_run_die_missing[@]}" -ne 0 ]; then
  ## Cannot use log/die here - that's exactly what we are failing
  ## to bootstrap. Plain printf to stderr.
  printf '%s\n' \
    "log_run_die.sh: ERROR: required command(s) not on PATH: ${__log_run_die_missing[*]}" \
    "log_run_die.sh: ERROR:   sourced by: ${BASH_SOURCE[1]:-<unknown>}" \
    "log_run_die.sh: ERROR:   top-level script: ${BASH_SOURCE[-1]:-${0:-<unknown>}}" \
    >&2
  ## Use 'return 1' rather than 'exit 1'. Callers are expected to
  ## run under errexit (R-010 strict-mode quintet); the non-zero
  ## return from 'source' then trips errexit and the caller's ERR
  ## trap fires - that is what does proper cleanup. In particular,
  ## derivative-maker's help-steps/pre installs an ERR trap that
  ## unmounts /raw / unchroots / removes the local temp apt repo
  ## before exiting the build; an unconditional 'exit 1' here
  ## would bypass that trap and leave the build environment in a
  ## half-mounted state. A caller that has not enabled errexit
  ## will walk past the failed source statement - that is a bug
  ## in the caller, not something this file should paper over.
  return 1
fi
unset __log_run_die_missing __log_run_die_cmd

## Suspend xtrace ('set -x') around blocks whose stdout we want to
## capture into a variable WITHOUT the xtrace traces of the inner
## commands polluting that capture. Use sparingly - prefer
## 'local -; set +x' inside a function (per agents/bash-style-guide.md).
##
## Pair: disable_xtrace then 'trap xtrace_reenable_maybe RETURN' at
## the top of the function so xtrace is restored to its prior state
## on every exit path (return, die, fall-through).
##
## Mirrors Kicksecure/helper-scripts/log_run_die.sh's definitions so
## test_run_as_target_user (in root_cmd.sh, which uses these) keeps
## working when the standalone is generated against this fork.
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

  ## Suppress xtrace for this function; local - saves and restores shell
  ## options automatically on every exit path (return, die, fall-through).
  local -
  set +x

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
  log_content="$(printf '%s' "${log_content}" | sanitize-string -- "${LOG_MAX_LEN:-nolimit}")"
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
  log error "Aborting."
  exit "${1}"
}


## Exit with an error if any of the listed commands are not available.
## usage: die_if_not_has cmd1 [cmd2 ...]
die_if_not_has() {
  local cmd

  for cmd in "$@"; do
    has "${cmd}" || die 1 "Required command not found: '${cmd}'"
  done
}


## Wrapper to log command before running to avoid duplication of code
log_run() {
  local level command_without_extraneous_spaces_temp command_without_extraneous_spaces
  level="${1}"
  shift || true

  printf -v command_without_extraneous_spaces_temp '%q ' "${@}"
  command_without_extraneous_spaces="$(printf "%s\n" "${command_without_extraneous_spaces_temp}")"

  ## TODO: rename variable to 'dry_run_skip_commands'. Potential footgun if used from other scripts.
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
    ## TODO: '|| return 1' needed?
    "${@}" || return 1
  fi
}


## Useful to get runtime mid run to log easily
## Variable to define outside: start_time
# shellcheck disable=SC2154
get_elapsed_time() {
  if ! is_integer "${start_time}"; then
    start_time=0
  fi
  printf '%s\n' "$(($(date +%s) - start_time))"
}


## Log elapsed time, the name explains itself.
log_time() {
  log info "Time elapsed: $(get_elapsed_time)s."
}
