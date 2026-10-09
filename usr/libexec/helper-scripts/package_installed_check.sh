#!/bin/sh

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## style-ok: no-strict - sourced library.

## 'local' is not in POSIX proper but is supported by every shell this ships
## on (bash, busybox, dash).
# shellcheck disable=SC3043

## NOTE: Must not include bashisms!

## NOTE: Fully installed packages only!
##       'dpkg-query' output 'install ok installed' only.

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
   status=$(printf '%s' "${dpkg_query_output}" | awk '{print $2}')
   error_state=$(printf '%s' "${dpkg_query_output}" | awk '{print $3}')

   if ! [ "${requested_action}" = 'install' ]; then
      true "$0: INFO: package ${package_name} requested_action ${requested_action} is not 'install'."
      return 1
   fi
   if ! [ "${status}" = 'ok' ]; then
      true "$0: INFO: package ${package_name} requested_action ${status} is not 'ok'."
      return 1
   fi
   if ! [ "${error_state}" = 'installed' ]; then
      true "$0: INFO: package ${package_name} requested_action ${error_state} is not 'installed'."
      return 1
   fi

   true "$0: INFO: ${package_name} is installed, ok."
   return 0
}
