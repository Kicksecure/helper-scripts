#!/bin/bash

## Copyright (C) 2024 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## https://github.com/anordal/shellharden/blob/master/how_to_do_things_safely_in_bash.md#echo--printf
## https://unix.stackexchange.com/questions/65803/why-is-printf-better-than-echo

safe_echo_type_of_printf="$(type -t printf)"

if [ ! "$safe_echo_type_of_printf" = "builtin" ]; then
  printf '%s\n' "ERROR: $0: printf is not a builtin" >&2
  exit 1
fi

safe_echo() {
    printf '%s\n' "$*"
}

safe_echo_nonewline() {
    printf '%s' "$*"
}
