#/bin/bash

## This is just a simple wrapper around 'command -v' to avoid
## spamming '>/dev/null' throughout this function. This also guards
## against aliases and functions.
## https://github.com/dylanaraps/pfetch/blob/pfetch#L53
has(){
  _cmd="$(command -v "${1}")" 2>/dev/null || return 1
  [ -x "${_cmd}" ] || return 1
}
