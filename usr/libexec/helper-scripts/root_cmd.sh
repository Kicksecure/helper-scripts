#!/bin/bash

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

source /usr/libexec/helper-scripts/get_colors.sh
source /usr/libexec/helper-scripts/log_run_die.sh

## Wrapper that supports su, sudo, doas
root_cmd(){
  local cmdarr

  test -z "${1:-}" && die 1 "${underline}root_cmd function:${nounderline} Failed to pass arguments to function 'root_cmd'."
  if test -z "${sucmd:-}"; then
    get_su_cmd
  fi
  : "${root_cmd_loglevel:=echo}"
  case "${sucmd}" in
    su)
      ## Thanks to Congelli501 for su to not mess with quotes.
      ## https://stackoverflow.com/a/32966744/2605155
      cmd="$(which -- "${1}")"
      shift
      log_run "$root_cmd_loglevel" su root -s "${cmd}" -- "${@}"
      ;;
    sudo)
      cmdarr=( 'log_run' "$root_cmd_loglevel" 'sudo' )
      if [ -n "$ROOT_CMD_TARGET_USER" ]; then
        cmdarr+=( '--user' "$ROOT_CMD_TARGET_USER" );
      fi
      if [ -n "$ROOT_CMD_TARGET_DIR" ]; then
        cmdarr+=( '--chdir' "$ROOT_CMD_TARGET_DIR" );
      fi
      cmdarr+=( '--' "${@}" )
      "${cmdarr[@]}"
      ;;
    doas)
      log_run "$root_cmd_loglevel" doas -u root -- "${@}"
      ;;
    *)
      die 1 "${underline}root_cmd function:${nounderline} 'root_cmd' does not support sucmd: '${sucmd}'"
      ;;
  esac
}


get_su_cmd(){
  export ROOT_CMD_TARGET_USER=''
  export ROOT_CMD_TARGET_DIR=''
  while true; do
    has sudo && sucmd=sudo && break
    has doas && sucmd=doas && break
    has su && sucmd=su && break
    [ -z "${sucmd:-}" ] && sucmd=''
    test -z "${sucmd}" && {
      if pkg_installed user-sysmaint-split; then
        die 1 "${underline}get_su_cmd:${nounderline} Failed to find program to run commands with administrative ('root') privileges. Package 'user-sysmaint-split' detected. You need to boot into sysmaint session."
      fi
      die 1 "${underline}get_su_cmd:${nounderline} Failed to find program to run commands with administrative ('root') privileges. This program requires either one of the following programs to be installed:
- sudo (recommended)
- doas
- su"
    }
    case "${sucmd}" in
      sudo) :;;
      *) log warn "Using sucmd '$sucmd'. Consider installation of 'sudo' instead to cache your passwords instead of typing them every time.";;
    esac
  done

  log info "Testing 'root_cmd' function..."
  root_cmd printf '%s\n' "test" >/dev/null ||
    die 1 "${underline}get_su_cmd:${nounderline} Failed to run test command as 'root'."

  if test "${ci:-}" = "1"; then
    root_output="$(timeout --kill-after 5 5 sudo --non-interactive -- test -d /usr 2>&1)"
    if test -n "${root_output}"; then
      log error "'sudo' output: '${root_output}'"
      die 1 "${underline}get_su_cmd:${nounderline} Unexpected non-empty output for 'sudo' test in CI mode."
    fi
    return 0
  fi

  ## Other su cmds do not have an option that does the same.
  if test "${sucmd}" = "sudo"; then
    if ! timeout --kill-after 5 5 sudo --non-interactive -- test -d /usr; then
      log warn "Credential Caching Status: 'No' - Without credential caching, this program will prompt for 'sudo' authorization multiple times. Consider configuring 'sudo' credential caching to streamline the installation process."
      return 0
    fi
    ## Used by dist-installer-gui.
    # shellcheck disable=SC2034
    credential_caching_status=yes
    log info "Credential Caching Status: 'Yes'"
    root_output="$(timeout --kill-after 5 5 sudo -- test -d /usr 2>&1)"
    if test -n "${root_output}"; then
      log error "'sudo' output: '${root_output}'"
      die 1 "${underline}get_su_cmd:${nounderline} Unexpected non-empty output for 'sudo' test in normal mode."
    fi
  fi
}


test_run_as_target_user() {
  local root_output
  ## root_output would catch xtrace and hence variable root_output would be non-empty.
  ## Therefore disabling xtrace.
  disable_xtrace
  root_output="$(run_as_target_user timeout --kill-after 5 5 test -d /usr 2>&1)"
  re_enable_xtrace_maybe
  if test -n "${root_output}"; then
    die 1 "${underline}run_as_target_user:${nounderline} 'sudo -u ${target_user}' test produced unexpected output: '${root_output}'"
  fi
}


run_as_target_user() {
  if [ -z "${target_user}" ]; then
    "${@}"
  else
    ROOT_CMD_TARGET_USER="${target_user}" root_cmd "${@}"
  fi
}


run_as_target_user_and_dir() {
  local target_dir
  target_dir="${1:-}"
  [ -z "${target_dir}" ] && die 1 "Failed to provide directory name to 'run_as_target_user_and_dir'!"
  [ -z "${target_user}" ] && die 1 "Cannot use 'run_as_target_user_and_dir' if 'set_target_user_account' is not used first!"
  shift
  ROOT_CMD_TARGET_USER="${target_user}" ROOT_CMD_TARGET_DIR="${target_dir}" root_cmd "${@}"
}
