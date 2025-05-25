#!/bin/bash

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## Capitalize only the first char of a string.
capitalize_first_char(){
  printf '%s' "${1:-}" | awk '{$1=toupper(substr($1,0,1))substr($1,2)}1'
}
