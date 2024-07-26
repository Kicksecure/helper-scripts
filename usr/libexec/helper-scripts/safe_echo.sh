#!/bin/bash

## Copyright (C) 2024 - 2024 ENCRYPTED SUPPORT LP <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## https://github.com/anordal/shellharden/blob/master/how_to_do_things_safely_in_bash.md#echo--printf

safe_echo_type_of_printf="$(type -t printf)"

if [ ! "$safe_echo_type_of_printf" = "builtin" ]; then
  echo "INFO: $0: printf is not a builtin" >&2
  exit 1
fi

safe_echo() {
    printf '%s\n' "$*"
}

safe_echo_nonewline() {
    printf '%s' "$*"
}
