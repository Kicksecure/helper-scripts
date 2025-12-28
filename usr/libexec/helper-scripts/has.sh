#!/bin/bash

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## This is just a simple wrapper around 'command -v' to avoid
## spamming '>/dev/null' throughout this function. This also guards
## against aliases and functions.
## https://github.com/dylanaraps/pfetch/blob/pfetch#L53
has(){
  local _cmd
  _cmd="$(command -v "${1}")" 2>/dev/null || return 1
  [ -x "${_cmd}" ] || return 1
}
