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
