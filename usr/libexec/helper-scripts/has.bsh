#!/bin/bash

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## style-ok: no-strict - sourced library.
## style-ok: no-has - this script is 'has' itself.

## This is just a simple wrapper around 'command -v' to avoid
## spamming '>/dev/null' throughout this function. This also guards
## against aliases and functions.
## https://github.com/dylanaraps/pfetch/blob/pfetch#L53
has() {
  local _cmd _name

  for _name in "$@"; do
    _cmd="$(command -v "${_name}")" 2>/dev/null || return 1
    ## TODO: Consider making it so that this command's only purpose is to check
    ## for executable files. In that instance we would want to error out if
    ## anything other than an absolute path is passed.
    case "${_cmd}" in
      /*)
        [ -x "${_cmd}" ] || return 1
        ;;
    esac
  done
}

is_type_file() {
  local _name

  for _name in "$@"; do
    if ! [ "$(type -t "${_name}")" = "file" ]; then
      return 1
    fi
  done
  return 0
}

type_exists() {
  local _name

  for _name in "$@"; do
    [ -n "$(type -t "${_name}")" ] || return 1
  done
  return 0
}

lsmod_deterministic() {
  lsmod | awk 'NR>1 {print $1}' | LC_ALL='C' sort
}

kernel_module_loaded_check() {
  lsmod_deterministic | grep --line-regexp --fixed-strings -- "${1}" >/dev/null
}

modprobe_remove() {
  if ! kernel_module_loaded_check "${1}"; then
    return 0
  fi
  modprobe --remove "${1}" || return 1
  return 0
}
