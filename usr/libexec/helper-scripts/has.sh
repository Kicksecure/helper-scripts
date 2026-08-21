#!/bin/bash

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## style-ok: no-strict -- this file is 'source'd, so a strict-mode block here
## would change the SOURCING shell's behaviour rather than apply to a shell of
## its own. The sourcer owns its strict-mode settings.
## style-ok: no-has -- this is the definition of 'has'; it cannot call itself.

## This is just a simple wrapper around 'command -v' to avoid
## spamming '>/dev/null' throughout this function. This also guards
## against aliases and functions.
## https://github.com/dylanaraps/pfetch/blob/pfetch#L53
has() {
  local _cmd _name

  for _name in "$@"; do
    _cmd="$(command -v "${_name}")" 2>/dev/null || return 1
    ## 'command -v' prints a bare word for builtins, functions, aliases and
    ## keywords rather than a path. Testing that word with '-x' would resolve
    ## it as a RELATIVE path in the current directory, so 'has printf' failed
    ## even though printf is always available. Only a path is worth testing.
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
