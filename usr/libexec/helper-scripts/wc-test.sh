#!/bin/bash

## Copyright (C) 2012 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

if ! printf '%s\n' "" | wc -l >/dev/null ; then
  printf '%s\n' "\
$0: ERROR: command 'wc' test failed! Do not ignore this!

'wc' can core dump. Example:
zsh: illegal hardware instruction (core dumped) wc -l
https://github.com/rspamd/rspamd/issues/5137" >&2
  exit 1
fi
