#!/bin/bash

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## This is just a simple wrapper around 'command -v' to avoid
## spamming '>/dev/null' throughout this function. This also guards
## against aliases and functions.
## https://github.com/dylanaraps/pfetch/blob/pfetch#L53
has() {
  local _cmd _name

  for _name in "$@"; do
    _cmd="$(command -v "${_name}")" 2>/dev/null || return 1
    [ -x "${_cmd}" ] || return 1
  done
}

is_type_file() {
  local _name

  for _name in "$@"; do
    if ! [ "$(type -t "${_name}")" = "file" ]; then
      return 1
    fi
  done
}

type_exists() {
  local _name

  for _name in "$@"; do
    [ "$(type -t "${_name}")" ] || return 1
  done
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
