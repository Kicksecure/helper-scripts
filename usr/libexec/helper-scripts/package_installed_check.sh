#!/bin/sh

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## style-ok: no-strict -- sourced library; a top-level strict-mode block
## would leak into the sourcing shell.

## 'local' is not in POSIX proper but is supported by every shell this ships
## on (dash, busybox); shellcheck's SC3043 is a portability nag, not a bug here.
# shellcheck disable=SC3043

## NOTE: Must not include bashisms!

## NOTE: code duplication: Function pkg_installed is duplicated elsewhere in derivative-maker source code.
pkg_installed() {
   ## 'local' does not break 'sh'.
   local package_name dpkg_query_output
   local requested_action status error_state

   package_name="$1"
   ## Cannot use '&>' because it is a bashism.
   dpkg_query_output="$(dpkg-query --show --showformat='${Status}' "${package_name}" 2>/dev/null)" || true
   ## dpkg_query_output Examples:
   ## install ok half-configured
   ## install ok installed

   requested_action=$(printf '%s' "${dpkg_query_output}" | awk '{print $1}')
   # shellcheck disable=SC2034
   status=$(printf '%s' "${dpkg_query_output}" | awk '{print $2}')
   # shellcheck disable=SC2034
   error_state=$(printf '%s' "${dpkg_query_output}" | awk '{print $3}')

   if [ "${requested_action}" = 'install' ]; then
      true "$0: INFO: ${package_name} is installed, ok."
      return 0
   fi

   true "$0: INFO: ${package_name} is not installed, ok."
   return 1
}
