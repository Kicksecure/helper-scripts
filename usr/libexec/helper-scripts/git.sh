#!/bin/bash

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

nothing_to_commit() {
   local nothing_to_commit_msg_one git_status_last_line
   nothing_to_commit_msg_one="nothing to commit, working tree clean"

   git_status_last_line="$(git status | tail -n1)" || true
   if [ "${git_status_last_line}" = "${nothing_to_commit_msg_one}" ]; then
      return 0
   fi
   return 1
}
