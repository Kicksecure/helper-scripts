#!/bin/bash

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  set -o errexit
  set -o nounset
  set -o errtrace
  set -o pipefail
fi

error_handler() {
  local exit_code="${?}"
  printf '%s\n' "\
BASH_COMMAND: ${BASH_COMMAND}
exit_code: ${exit_code}"
  exit "${exit_code}"
}

exit_handler() {
  [[ -v "exit_code" ]] || exit_code="0"
  printf '%s\n' ""
  if [ "$exit_code" = 0 ]; then
    printf '%s\n' "$0: INFO: OK."
  else
    printf '%s\n' "$0: ERROR: Exiting with code '$exit_code'." >&2

  fi
  exit "$exit_code"
}

## Checks to see if all items in "check_str" are present in the output of a
## command that lists valid items.
is_layout_data_valid() {
  local valid_list_cmd check_str check_lines check_list check_item \
    valid_output valid_item_list valid_item is_item_valid

  check_str="${1:-}"
  shift
  valid_list_cmd=( "$@" )
  if [ "${#valid_list_cmd[@]}" = '0' ] || [ -z "${valid_list_cmd[0]}" ]; then\
    return 1
  fi
  if [ -z "${check_str}" ]; then
    return 1
  fi

  check_lines=$(printf '%s\n' "${check_str}" | tr ',' '\n')
  readarray -t check_list <<< "${check_lines}"

  ## Should this ever fail, that would probably be a bug. In that case,
  ## consider this fatal and let the error_handler address it.
  valid_output=$("${timeout_command[@]}" "${valid_list_cmd[@]}")
  readarray -t valid_item_list <<< "${valid_output}"

  for check_item in "${check_list[@]}"; do
    if [ -z "${check_item}" ]; then continue; fi
    is_item_valid='false'
    for valid_item in "${valid_item_list[@]}"; do
      if [ "${check_item}" = "${valid_item}" ]; then
        is_item_valid='true'
        break
      fi
    done
    if [ "${is_item_valid}" = 'false' ]; then
      return 1
    fi
  done

  return 0
}

check_keyboard_layouts() {
  local layout_str kb_layout_list layout layout_arr

  layout_str="${1:-}"
  if [ -z "${layout_str}" ]; then
    printf '%s\n' "${FUNCNAME[0]}: ERROR: Empty keyboard layout string provided!" >&2
    return 1
  fi
  readarray -t layout_arr < <(printf '%s\n' "${layout_str}" | tr ',' '\n')
  for layout in "${layout_arr[@]}"; do
    if [ -z "${layout}" ]; then
      printf '%s\n' "${FUNCNAME[0]}: ERROR: Empty element found in keyboard layouts!" >&2
      return 1
    fi
  done

  ## Ensure the user has no more than four keyboard layouts specified (this
  ## is the maximum number supported by XKB under X11 according to
  ## https://www.x.org/archive/X11R7.5/doc/input/XKB-Config.html, and it is
  ## the maximum number labwc appears to support).
  readarray -t kb_layout_list < <(printf '%s\n' "${layout_str}" | tr ',' '\n')
  if (( ${#kb_layout_list[@]} > 4 )); then
    printf '%s\n' "${FUNCNAME[0]}: ERROR: Too many keyboard layouts specified, must specify 4 or less!" >&2
    return 1
  fi

  ## Ensure the specified keyboard layout(s) are valid.
  if ! is_layout_data_valid "${layout_str}" \
    localectl-static --no-pager list-x11-keymap-layouts ; then
    printf '%s\n' "${FUNCNAME[0]}: ERROR: Specified keyboard layout(s) '${layout_str}' are not all valid!" >&2
    if [ "${skl_interactive}" = 'false' ]; then
      printf '%s\n' "${FUNCNAME[0]}: INFO: Run 'localectl-static --no-pager list-x11-keymap-layouts' to get a list of valid layouts."
    fi
    return 1
  fi

  return 0
}

check_keyboard_layout_variants() {
  local layout_str variant_str kb_layout_list kb_variant_list kb_idx

  layout_str="${1:-}"
  variant_str="${2:-}"
  if [ -z "${layout_str}" ]; then
    printf '%s\n' "${FUNCNAME[0]}: ERROR: Empty keyboard layout string provided!" >&2
    return 1
  fi
  if [ -z "${variant_str}" ]; then
    printf '%s\n' "${FUNCNAME[0]}: ERROR: Empty keyboard layout variant string provided!" >&2
    return 1
  fi

  readarray -t kb_layout_list < <(printf '%s\n' "${layout_str}" | tr ',' '\n')
  ## Don't redo the keyboard layout count check, that's been done by
  ## function 'check_keyboard_layouts' already.
  readarray -t kb_variant_list < <(printf '%s\n' "${variant_str}" | tr ',' '\n')

  if (( ${#kb_layout_list[@]} < ${#kb_variant_list[@]} )); then
    printf '%s\n' "${FUNCNAME[0]}: ERROR: Insufficient number of keyboard layouts specified for number of variants!" >&2
    return 1
  fi

  if (( ${#kb_layout_list[@]} > ${#kb_variant_list[@]} )); then
    printf '%s\n' "${FUNCNAME[0]}: ERROR: Too many keyboard layouts specified for number of variants!" >&2
    return 1
  fi

  for kb_idx in "${!kb_layout_list[@]}"; do
    if [ -z "${kb_variant_list[kb_idx]}" ]; then continue; fi
    if ! is_layout_data_valid "${kb_variant_list[kb_idx]}" \
      localectl-static --no-pager list-x11-keymap-variants "${kb_layout_list[kb_idx]}" ; then
      printf '%s\n' "${FUNCNAME[0]}: ERROR: Specified keyboard layout variant '${kb_variant_list[kb_idx]}' for layout '${kb_layout_list[kb_idx]}' is not valid!" >&2
      if [ "${skl_interactive}" = 'false' ]; then
        printf '%s\n' "${FUNCNAME[0]}: INFO: Run 'localectl-static --no-pager list-x11-keymap-variants ${kb_layout_list[kb_idx]}' to get a list of valid layout variants for the '${kb_layout_list[kb_idx]}' layout."
      fi
      return 1
    fi
  done
}

check_keyboard_layout_options() {
  local option_str option_arr option

  option_str="${1:-}"
  if [ -z "${option_str}" ]; then
    printf '%s\n' "${FUNCNAME[0]}: ERROR: Empty keyboard layout options string provided!" >&2
    return 1
  fi
  readarray -t option_arr < <(printf '%s\n' "${option_str}" | tr ',' '\n')
  for option in "${option_arr[@]}"; do
    if [ -z "${option}" ]; then
      printf '%s\n' "${FUNCNAME[0]}: ERROR: Empty element found in keyboard layout options!" >&2
      return 1
    fi
  done

  if ! is_layout_data_valid "${option_str}" \
    localectl-static --no-pager list-x11-keymap-options ; then
    printf '%s\n' "${FUNCNAME[0]}: ERROR: Specified keyboard layout option(s) are not valid!" >&2
    if [ "${skl_interactive}" = 'false' ]; then
      printf '%s\n' "${FUNCNAME[0]}: INFO: Run 'localectl-static --no-pager list-x11-keymap-options' to get a list of valid layout options."
    fi
    return 1
  fi
}

## Replaces the variables specified in the given file with new values,
## removing duplicates and appending new variables.
replace_file_variables() {
  local file_contents file_lines var_names var_values var_idx \
    did_replace_var conf_idx

  ## Parse command-line arguments
  file_contents="${1:-}"
  if [ -n "${file_contents}" ]; then
    readarray -t file_lines <<< "${file_contents}"
  else
    file_lines=()
  fi
  var_names=()
  var_values=()
  shift
  while [ -n "${1:-}" ]; do
    ## Note that variable names must never be empty, but it is legal for
    ## variable *values* to be empty.
    var_names+=( "${1:-}" )
    var_values+=( "${2:-}" )
    shift 2
  done
  if [ "${#var_names[@]}" = '0' ]; then
    printf '%s\n' "${FUNCNAME[0]}: ERROR: No new variables provided!" >&2
    return 1
  fi

  ## Loop through the lines of the existing labwc environment configuration.
  ## Change already-set keyboard-layout-related variables to new values,
  ## append variables that we want to set but that aren't defined yet. Remove
  ## duplicate variable assignments so that the variables we set don't get
  ## overridden.
  for var_idx in "${!var_names[@]}"; do
    did_replace_var='false'
    for conf_idx in "${!file_lines[@]}"; do
      ## Note that we use a capturing group around leading whitespace - this
      ## allows us to prepend ${BASH_REMATCH[1]} to the replacement line,
      ## preserving the indentation.
      if [[ "${file_lines[conf_idx]}" \
        =~ ^([[:space:]]*)"${var_names[var_idx]}=" ]]; then
        if [ "${did_replace_var}" = 'false' ]; then
          file_lines[conf_idx]="${BASH_REMATCH[1]}${var_names[var_idx]}=${var_values[var_idx]}"
          did_replace_var='true'
        else
          unset "file_lines[${conf_idx}]"
        fi
      fi
    done

    ## Remove any holes from the `file_lines` array.
    file_lines=( "${file_lines[@]}" )

    ## If we replaced a variable assignment in the configuration file, skip
    ## the rest of this loop iteration.
    if [ "${did_replace_var}" = 'true' ]; then
      continue
    fi

    ## Append the new environment variable to the configuration file's
    ## contents.
    file_lines+=( "${var_names[var_idx]}=${var_values[var_idx]}" )
  done

  printf '%s\n' "${file_lines[@]}"
}

## Sets the XKB layout(s), variant(s), and option(s) in 'labwc', either for just
## this session or persistently.
set_labwc_keymap() {
  local labwc_config_bak_path var_idx labwc_env_file_string \
    labwc_config_directory \
    calc_replace_args labwc_existing_config

  labwc_config_bak_path=''

  ## We must have at least one, but no more than three, arguments specifying the
  ## keyboard layout(s).
  if [ "${#args[@]}" = '0' ] || [ -z "${args[0]:-}" ] \
    || (( ${#args[@]} > 3 )); then
    ## The print_usage function is provided by the script that sources this
    ## library.
    print_usage
    exit 1
  fi

  ## If we have less than three arguments, populate the `args` array with empty
  ## strings for the remaining arguments. This will make 'labwc' unset the
  ## corresponding XKB environment variables internally, allowing the user to
  ## run something like `set-labwc-keymap us colemak`, then
  ## `set-labwc-keymap us` and have their keyboard not stuck in the Colemak
  ## layout after the second command.
  while (( ${#args[@]} < 3 )); do
    args+=( '' )
  done

  ## Interactive mode checks the layouts for us already, no need to do it
  ## twice.
  if [ "${skl_interactive}" = 'false' ]; then
    check_keyboard_layouts "${args[0]}" || return 1
    if [ -n "${args[1]:-}" ]; then
      check_keyboard_layout_variants "${args[0]}" "${args[1]}" || return 1
    fi
    if [ -n "${args[2]:-}" ]; then
      check_keyboard_layout_options "${args[2]}" || return 1
    fi
  fi

  if test -d "${labwc_config_path}"; then
    printf '%s\n' "${FUNCNAME[0]}: ERROR: --config='${labwc_config_path}' is a folder but should be a file!" >&2
    return 1
  fi

  labwc_config_directory="$(dirname -- "${labwc_config_path}")"

  ## Ensure the 'labwc' configuration directory exists.
  if ! mkdir --parents -- "${labwc_config_directory}" ; then
    printf '%s\n' "${FUNCNAME[0]}: ERROR: Cannot create 'labwc' config directory '${labwc_config_directory}'!" >&2
    return 1
  fi

  ## If 'labwc's environment config file exists, read it.
  labwc_existing_config=''
  if [ -f "${labwc_config_path}" ]; then
    if ! [ -r "${labwc_config_path}" ]; then
      printf '%s\n' "${FUNCNAME[0]}: ERROR: No read permissions on 'labwc' environment config '${labwc_config_path}'!" >&2
      return 1
    fi

    if ! labwc_existing_config="$(cat -- "${labwc_config_path}")" ; then
      printf '%s\n' "${FUNCNAME[0]}: ERROR: Cannot read existing 'labwc' environment config '${labwc_config_path}'!" >&2
      return 1
    fi

    ## If we do not want the new configuration to be persistent, move the
    ## existing configuration to a temporary backup location.
    if [ "${do_persist}" = 'false' ]; then
      labwc_config_bak_path="$(mktemp)"
      if ! mv -- "${labwc_config_path}" "${labwc_config_bak_path}" ; then
        printf '%s\n' "${FUNCNAME[0]}: ERROR: Cannot move existing 'labwc' environment config '${labwc_config_path}' to backup location '${labwc_config_bak_path}'!" >&2
        return 1
      fi
    fi

    calc_replace_args=( "${labwc_existing_config}" )
  else
    calc_replace_args=( '' )
  fi

  for var_idx in "${!args[@]}"; do
    calc_replace_args+=(
      "${skl_xkb_env_var_names[var_idx]}"
      "${args[var_idx]}"
    )
  done

  labwc_env_file_string="$(replace_file_variables "${calc_replace_args[@]}")"

  ## Write the new config file contents and load them into 'labwc'.
  if ! overwrite "${labwc_config_path}" "${labwc_env_file_string}" >/dev/null ; then
    printf '%s\n' "${FUNCNAME[0]}: ERROR: Cannot write new 'labwc' environment config '${labwc_config_path}'!" >&2
    return 1
  fi

  if [ "${no_reload}" = 'false' ]; then
    if ischroot --default-false; then
      printf '%s\n' "${FUNCNAME[0]}: INFO: Skipping executing 'labwc --reconfigure' inside chroot, ok."
    elif pgrep -- labwc >/dev/null; then
      ## 'labwc' is running. So the user most likely wishes the change to instantly apply.
      ## Therefore let's run 'labwc --reconfigure'.
      if ! command -v labwc >/dev/null; then
        ## This would be weird. 'labwc' is running but unavailable in the PATH environment variable.
        printf '%s\n' "${FUNCNAME[0]}: ERROR: The 'labwc' program is unavailable in the PATH environment variable or not installed." >&2
      else
        ## 'labwc' is running and available in the PATH environment variable.
        if labwc --reconfigure; then
          printf '%s\n' "${FUNCNAME[0]}: INFO: 'labwc --reconfigure' OK."
        else
          printf '%s\n' "${FUNCNAME[0]}: WARNING: 'labwc --reconfigure' reconfiguration failed!"
        fi
      fi
    else
      printf '%s\n' "${FUNCNAME[0]}: INFO: 'labwc' not running, no need to execute 'labwc --reconfigure', OK."
    fi
  fi

  ## If we do not want to persist the new configuration, put the old
  ## configuration back (or just delete the new config file if there wasn't an
  ## old config file).
  if [ -n "${labwc_config_bak_path}" ]; then
    printf '%s\n' "${FUNCNAME[0]}: INFO: ephemeral '${labwc_config_path}' contents:"
    stcat "${labwc_config_path}"
    if ! mv -- "${labwc_config_bak_path}" "${labwc_config_path}" ; then
      printf '%s\n' "${FUNCNAME[0]}: ERROR: Cannot move backup 'labwc' environment config '${labwc_config_bak_path}' to original location '${labwc_config_path}'!" >&2
      return 1
    fi
  elif [ "${do_persist}" = 'true' ]; then
    printf '%s\n' "${FUNCNAME[0]}: INFO: new '${labwc_config_path}' contents:"
    stcat "${labwc_config_path}"
  elif [ "${do_persist}" = 'false' ]; then
    printf '%s\n' "${FUNCNAME[0]}: INFO: Non-persistent configuration done. To persist, omit option: --no-persist"
    if ! safe-rm -- "${labwc_config_path}" ; then
      printf '%s\n' "${FUNCNAME[0]}: ERROR: Cannot remove temporary 'labwc' environment config '${labwc_config_path}'!" >&2
      return 1
    fi
  fi

  ## Can be for 'labwc' or 'greetd'.
  printf '%s\n' "${FUNCNAME[0]}: INFO: Configuration success."
}

dpkg_reconfigure_function() {
  local dpkg_reconfigure_exit_code dpkg_reconfigure_output_original \
    dpkg_reconfigure_output_filtered
  printf '%s\n' "${FUNCNAME[0]}: EXECUTING: '${*}'"
  dpkg_reconfigure_exit_code=0
  dpkg_reconfigure_output_original="$("${@}" 2>&1)" || { dpkg_reconfigure_exit_code="$?"; true; }
  ## dpkg-reconfigure can cause the following error message:
  ## (This however does not cause a non-zero exit code.)
  #cat: '/sys/bus/usb/devices/*:*/bInterfaceClass': No such file or directory
  #cat: '/sys/bus/usb/devices/*:*/bInterfaceSubClass': No such file or directory
  #cat: '/sys/bus/usb/devices/*:*/bInterfaceProtocol': No such file or directory
  dpkg_reconfigure_output_filtered="$(
    printf '%s\n' "${dpkg_reconfigure_output_original}" |
      sed "\|^cat: '/sys/bus/usb/devices/\*:\*/bInterface|d"
  )"
  if [ "${dpkg_reconfigure_output_filtered}" = "" ]; then
    printf '%s\n' "${FUNCNAME[0]}: INFO: OK."
  else
    printf '%s\n' "${dpkg_reconfigure_output_filtered}" >&2
  fi
  exit_code="${dpkg_reconfigure_exit_code}"
  ## Always 'return 0', because even if the dpkg-configure command failed, this is considered an
  ## insufficient reason to stop this script at this point.
  return 0
}

dracut_run() {
  if ischroot --default-false; then
    ## Inside chroot such as during image builds it may be best to leave running dracut to the build tool.
    printf '%s\n' "${FUNCNAME[0]}: INFO: Skipping command 'dracut --regenerate-all --force' inside chroot, ok."
    return 0
  fi
  if ! command -v dracut >/dev/null; then
    printf '%s\n' "${FUNCNAME[0]}: WARNING: Minor issue. The 'dracut' program is unavailable in the PATH environment variable or not installed. Keyboard layout in initramfs unchanged."
    return 0
  fi
  printf '%s\n' "${FUNCNAME[0]}: INFO: Rebuilding all dracut initramfs images... This will take a while..."
  printf '%s\n' "${FUNCNAME[0]}: EXECUTING: 'dracut --regenerate-all --force'"
  if dracut --regenerate-all --force &>/dev/null; then
    printf '%s\n' "${FUNCNAME[0]}: INFO: Rebuilding all initramfs images was successful."
  else
    printf '%s\n' "${FUNCNAME[0]}: ERROR: Rebuilding all initramfs images was failed! Your system might be unbootable! This issue is very most likely not caused by '$0'. Please manually run 'sudo dracut --regenerate-all --force' to see this error for yourself." >&2
    exit_code=1
  fi
}

## Sets the XKB layout(s), variant(s), and option(s) for the console. Due to
## limitations in Linux, this is a system-wide setting only.
##
## Quote 'man setupcon':
##   The keyboard configuration is specified in ~/.keyboard or /etc/default/keyboard.
##
## However, this does not help much because even if '~/.keyboard' still 'setupcon'
## cannot be run without root rights.
## It may be possible to set 'setupcon' (or 'loadkeys'?) SUID, however this is unwanted
## for security reasons.
## https://www.kicksecure.com/wiki/SUID_Disabler_and_Permission_Hardener
## A 'privleap' rule could be configured to allow non-root executing 'setupcon' but 'setupcon'
## applies globally, not only per-user. Therefore the virtual console keyboard layout for
## other users might also be changed.
## Configuration of the '~/.keyboard' file may or may not be applicable during the 'login' program.
## It has therefore been decided, not to implement non-root virtual console keyboard layout changes.
##
## https://unix.stackexchange.com/questions/85374/loadkeys-gives-permission-denied-for-normal-user
##
## NOTE: Changes will take effect after a reboot. This is because CLI keyboard
## layout changes would need to be applied with 'setupcon', but 'setupcon' may not
## be safe to use to apply CLI keyboard layout changes while a graphical
## session is active. Quoting the manpage for 'setupcon':
##
##   --force
##     Do not check whether we are on the console. Notice that you can be
##     forced to hard-reboot your computer if you run setupcon with this
##     option and the screen is controlled by a X server.
set_console_keymap() {
  local var_idx kb_conf_file_string kb_conf_path kb_conf_dir \
    calc_replace_args dpkg_reconfigure_command

  printf '%s\n' "${FUNCNAME[0]}: INFO: Console keymap configuration..."

  ## Parse command line arguments
  kb_conf_dir='/etc/default'
  kb_conf_path="${kb_conf_dir}/keyboard"

  ## We must have at least one, but no more than three, arguments specifying the
  ## keyboard layout(s).
  if [ "${#args[@]}" = '0' ] || [ -z "${args[0]:-}" ] \
    || (( ${#args[@]} > 3 )); then
    ## The print_usage function is provided by the script that sources this
    ## library.
    print_usage
    exit 1
  fi

  ## If we have less than three arguments, populate the `args` array with empty
  ## strings for the remaining arguments.
  while (( ${#args[@]} < 3 )); do
    args+=( '' )
  done

  ## Interactive mode checks the layouts for us already, no need to do it
  ## twice.
  if [ "${skl_interactive}" = 'false' ]; then
    check_keyboard_layouts "${args[0]}" || return 1
    if [ -n "${args[1]:-}" ]; then
      check_keyboard_layout_variants "${args[0]}" "${args[1]}" || return 1
    fi
    if [ -n "${args[2]:-}" ]; then
      check_keyboard_layout_options "${args[2]}" || return 1
    fi
  fi

  if ! mkdir --parents -- "${kb_conf_dir}" ; then
    printf '%s\n' "${FUNCNAME[0]}: ERROR: Cannot ensure the existence of '${kb_conf_dir}'!" >&2
    return 1
  fi

  if [ -f "${kb_conf_path}" ]; then
    calc_replace_args=( "$(cat -- "${kb_conf_path}")" ) || return 1
  else
    calc_replace_args=( '' )
  fi
  for var_idx in "${!args[@]}"; do
    calc_replace_args+=(
      "${skl_default_keyboard_var_names[var_idx]}"
      "${args[var_idx]}"
    )
  done

  kb_conf_file_string="$(replace_file_variables "${calc_replace_args[@]}")"

  ## Write the new config file contents.
  if ! overwrite "${kb_conf_path}" "${kb_conf_file_string}" >/dev/null ; then
    printf '%s\n' "${FUNCNAME[0]}: ERROR: Cannot write new keyboard config file '${kb_conf_path}'!" >&2
    return 1
  fi

  printf '%s\n' "${FUNCNAME[0]}: INFO: new '${kb_conf_path}' contents:"
  stcat "${kb_conf_path}"

  dpkg_reconfigure_command=( "dpkg-reconfigure" "--frontend=noninteractive" "keyboard-configuration" )
  ## Test error handling.
  #dpkg_reconfigure_command=( "dpkg-reconfigure" )
  ## Apply the changes to the config file to the system.
  dpkg_reconfigure_function "${dpkg_reconfigure_command[@]}"

  if ischroot --default-false; then
    printf '%s\n' "${FUNCNAME[0]}: INFO: Skipping command 'systemctl --no-block --no-pager restart keyboard-setup.service' inside chroot, ok."
    return 0
  fi

  ## TODO: Do not try this if not running as root.
  if "${timeout_command[@]}" systemctl --no-block --no-pager status keyboard-setup.service &>/dev/null; then
    printf '%s\n' "${FUNCNAME[0]}: EXECUTING: 'systemctl --no-block --no-pager restart keyboard-setup.service'"
    if "${timeout_command[@]}" systemctl --no-block --no-pager restart keyboard-setup.service; then
      printf '%s\n' "${FUNCNAME[0]}: INFO: Restart of systemd unit 'keyboard-setup.service' success."
    else
      printf '%s\n' "${FUNCNAME[0]}: WARNING: Restart of systemd unit 'keyboard-setup.service' failed. Reboot may be required to change the virtual console keyboard layout."
    fi
  else
    printf '%s\n' "${FUNCNAME[0]}: WARNING: Systemd unit 'keyboard-setup.service' is not running or does not exist. Reboot may be required to change the virtual console keyboard layout."
  fi

  printf '%s\n' "${FUNCNAME[0]}: INFO: system console configuration success."
}

## NOTE: This function assumes it is run as root.
kb_reload_root() {
  local loginctl_users_json user_list uid_list user_name uid wl_sock wl_pid wl_comm account_name counter

  printf '%s\n' "${FUNCNAME[0]}: INFO: Reloading keyboard layout..."

  if ischroot --default-false; then
    printf '%s\n' "${FUNCNAME[0]}: INFO: Skipping sending SIGHUP to 'labwc' inside chroot, ok."
    return 0
  fi

  ## The only easily machine-readable format 'loginctl' can output the user list
  ## in is json. We could also use
  ## `loginctl list-users --no-pager | tail -n+2 | head -n+2 | cut -d' ' -f2`
  ## if the dependency on 'jq' is undesirable, but this will probably break if a
  ## future 'systemd' update changes the output format.

  ## Avoid subshell for better error handling.
  #readarray -t user_list < <(loginctl -j list-users | jq -r '.[] | .user')

  loginctl_users_json="$(
    "${timeout_command[@]}" \
      loginctl -j list-users
  )" || true

  if [ "$loginctl_users_json" = "" ]; then
    printf '%s\n' "${FUNCNAME[0]}: WARNING: Minor issue. 'loginctl -j list-users' returned no users. Reboot may be required to change the graphical (Wayland / 'labwc') keyboard layout."
    return 0
  fi

  loginctl_users_parsed="$(jq -r '.[] | .user' <<< "$loginctl_users_json")" || true

  if [ "$loginctl_users_parsed" = "" ]; then
    printf '%s\n' "${FUNCNAME[0]}: WARNING: Minor issue. Failed to parse 'loginctl_users_json' using 'jq'.
loginctl_users_json: '$loginctl_users_json'
Reboot may be required to change the graphical (Wayland / 'labwc') keyboard layout."
    return 0
  fi

  user_list=()
  while IFS= read -r line; do
    user_list+=("$line")
  done <<< "$loginctl_users_parsed"

  true "user_list: ${user_list[*]}"

  uid_list=()
  for user_name in "${user_list[@]}"; do
    uid_list+=( "$(id --user -- "${user_name}")" )
  done

  counter=0
  for uid in "${uid_list[@]}"; do
    for wl_sock in "/run/user/${uid}/wayland-"*; do
      if ! [ -S "${wl_sock}" ]; then
        continue
      fi

      wl_pid="$(/usr/libexec/helper-scripts/query-sock-pid "${wl_sock}")" || true
      if [ -z "${wl_pid:-}" ]; then
        continue
      fi

      wl_comm="$(cat -- "/proc/${wl_pid}/comm")" || true
      if [ -z "${wl_comm:-}" ]; then
        continue
      fi

      account_name="$(id --name --user -- "${uid}")"

      if [ "${wl_comm}" = 'labwc' ]; then
        counter=$(( counter + 1))
        ## From the labwc manpage:
        ##
        ## -r, --reconfigure
        ##     Reload the compositor configuration by sending SIGHUP to
        ##     `$LABWC_PID`
        ##
        ## Therefore, `kill -s SIGHUP -- "${wl_pid}"` is the same as
        ## `LABWC_PID="${wl_pid}" labwc --reconfigure`, but shorter, probably
        ## faster, and doesn't require environment variables.
        ##
        ## Unfortunately, this will not reconfigure all running labwc
        ## instances, it will only reconfigure the one running on the active
        ## TTY. See:
        ## https://github.com/labwc/labwc/issues/3184
        ##
        ## 'kill' is a shell built-in and does not support long option '--signal'.
        if kill -s 0 -- "${wl_pid}"; then
          printf '%s\n' "${FUNCNAME[0]}: INFO: Sending signal SIGHUP for account '${account_name}' to process 'labwc' pid '${wl_pid}' to trigger configuration reload..."
          if kill -s SIGHUP -- "${wl_pid}"; then
            printf '%s\n' "${FUNCNAME[0]}: INFO: Signal SIGHUP ok."
          else
            printf '%s\n' "${FUNCNAME[0]}: WARNING: Minor issue. Sending signal SIGHUP failed. Reboot may be required to change the graphical (Wayland / 'labwc') keyboard layout."
          fi
        else
          printf '%s\n' "${FUNCNAME[0]}: WARNING: Minor issue. Not sending signal SIGHUP for account '${account_name}' to process 'labwc' pid '${wl_pid}' because it is not running. Reboot may be required to change the graphical (Wayland / 'labwc') keyboard layout."
        fi
      fi
    done
  done

  if [ "$counter" = 0 ]; then
    printf '%s\n' "${FUNCNAME[0]}: INFO: No need to send SIGHUP to 'labwc' because none running."
  fi
}

## Sets the system-wide keyboard layout for the console, greeter, and labwc
## sessions all at once.
set_system_keymap() {
  local labwc_system_wide_config_dir labwc_system_wide_config_path \
    labwc_greeter_config_dir labwc_greeter_config_path

  ## We must have at least one, but no more than three, arguments specifying the
  ## keyboard layout(s).
  if [ "${#args[@]}" = '0' ] || [ -z "${args[0]:-}" ] \
    || (( ${#args[@]} > 3 )); then
    ## The print_usage function is provided by the script that sources this
    ## library.
    print_usage
    exit 1
  fi

  ## If we have less than three arguments, populate the `args` array with empty
  ## strings for the remaining arguments.
  while (( ${#args[@]} < 3 )); do
    args+=( '' )
  done

  labwc_system_wide_config_dir='/etc/xdg/labwc'
  labwc_system_wide_config_path="${labwc_system_wide_config_dir}/environment"
  labwc_greeter_config_dir='/etc/greetd/labwc-config'
  labwc_greeter_config_path="${labwc_greeter_config_dir}/environment"

  if ! mkdir --parents -- "${labwc_system_wide_config_dir}" ; then
    printf '%s\n' "${FUNCNAME[0]}: ERROR: Cannot ensure the existence of '${labwc_system_wide_config_dir}'!" >&2
    return 1
  fi
  if ! mkdir --parents -- "${labwc_greeter_config_dir}" ; then
    printf '%s\n' "${FUNCNAME[0]}: ERROR: Cannot ensure the existence of '${labwc_greeter_config_dir}'!" >&2
    return 1
  fi

  set_console_keymap \
    "${args[@]}" \
    || return 1
  printf '%s\n' ""

  ## {{{ Set the specified keyboard layout for labwc both system-wide and for the greeter.

  printf '%s\n' "${FUNCNAME[0]}: INFO: 'labwc' configuration..."

  labwc_config_path="${labwc_system_wide_config_path}" \
    set_labwc_keymap \
    "${args[@]}" \
    || return 1
  printf '%s\n' ""

  printf '%s\n' "${FUNCNAME[0]}: INFO: 'greetd' configuration..."
  labwc_config_path="${labwc_greeter_config_path}" \
    set_labwc_keymap \
    "${args[@]}" \
    || return 1
  printf '%s\n' ""

  ## }}}

  set_grub_keymap \
    "${args[@]}" \
    || return 1
  printf '%s\n' ""

  kb_reload_root
  printf '%s\n' ""

  dracut_run
  printf '%s\n' ""

  printf '%s\n' "${FUNCNAME[0]}: INFO: Keyboard layout change successful."
}

rebuild_grub_config() {
  local update_grub_output

  if ischroot --default-false; then
    ## Inside chroot such as during image builds it may be best to leave running update-grub to the build tool.
    printf '%s\n' "${FUNCNAME[0]}: INFO: Skipping command 'update-grub' inside chroot, ok."
    return 0
  fi

  if ! command -v 'update-grub' >/dev/null 2>&1; then
    printf '%s\n' "${FUNCNAME[0]}: ERROR: Cannot proceed with updating GRUB configuration because requirements are unavailable. The 'update-grub' program is unavailable in the PATH environment variable or not installed. Is package 'grub2-common' installed?" >&2
    return 1
  fi

  printf '%s\n' "${FUNCNAME[0]}: INFO: Rebuilding GRUB configuration... This will take a moment..."
  printf '%s\n' "${FUNCNAME[0]}: EXECUTING: 'update-grub'"
  if ! update_grub_output="$(update-grub 2>&1)"; then
    printf '%s\n' "${FUNCNAME[0]}: ERROR: Failed to update GRUB configuration! Your system might be unbootable! This issue is very most likely not caused by '$0'. Please manually run 'sudo update-grub' to see this error for yourself." >&2
    printf '%s\n' "${FUNCNAME[0]}: Output from command 'update-grub':" >&2
    printf '%s\n' "${update_grub_output}" >&2
    return 1
  fi
}

set_grub_keymap() {
  local grub_kbdcomp_output name_part_list name_part

  printf '%s\n' "${FUNCNAME[0]}: INFO: GRUB keymap configuration..."

  ## We must have at least one, but no more than three, arguments specifying the
  ## keyboard layout(s).
  if [ "${#args[@]}" = '0' ] || [ -z "${args[0]:-}" ] \
    || (( ${#args[@]} > 3 )); then
    ## The print_usage function is provided by the script that sources this
    ## library.
    print_usage
    exit 1
  fi

  ## If we have less than three arguments, populate the `args` array with empty
  ## strings for the remaining arguments.
  while (( ${#args[@]} < 3 )); do
    args+=( '' )
  done

  ## Interactive mode checks the layouts for us already, no need to do it
  ## twice.
  if [ "${skl_interactive}" = 'false' ]; then
    check_keyboard_layouts "${args[0]}" || return 1
    if [ -n "${args[1]:-}" ]; then
      check_keyboard_layout_variants "${args[0]}" "${args[1]}" || return 1
    fi
    if [ -n "${args[2]:-}" ]; then
      check_keyboard_layout_options "${args[2]}" || return 1
    fi
  fi

  if ! mkdir --parents -- "${grub_kb_layout_dir}"; then
    printf '%s\n' "${FUNCNAME[0]}: ERROR: Cannot create GRUB keyboard layout dir '${grub_kb_layout_dir}'!" >&2
    return 1
  fi

  if ! command -v 'grub-kbdcomp' >/dev/null 2>&1; then
    printf '%s\n' "${FUNCNAME[0]}: ERROR: Cannot proceed with generating GRUB keymap because requirements are unavailable. The 'grub-kbdcomp' program is unavailable in the PATH environment variable or not installed. Is package 'grub-common' installed?" >&2
    return 1
  fi

  ## /usr/bin/grub-kbdcomp: 76: ckbcomp: not found
  if ! command -v 'ckbcomp' >/dev/null 2>&1; then
    printf '%s\n' "${FUNCNAME[0]}: ERROR: Cannot proceed with generating GRUB keymap because requirements are unavailable. The 'ckbcomp' program is unavailable in the PATH environment variable or not installed. Is package 'console-setup' or 'console-setup-mini' installed?" >&2
    return 1
  fi

  printf '%s\n' "${FUNCNAME[0]}: INFO: Generating GRUB keymap..."
  printf '%s\n' "${FUNCNAME[0]}: EXECUTING: 'grub-kbdcomp -o ${grub_kb_layout_dir}/user-layout.gkb ${args[*]}'"
  if ! grub_kbdcomp_output="$(
    grub-kbdcomp -o "${grub_kb_layout_dir}/user-layout.gkb" "${args[@]}" 2>&1
  )"; then
    printf '%s\n' "${FUNCNAME[0]}: ERROR: Failed to build GRUB keyboard layout!"
    printf '%s\n' "${FUNCNAME[0]}: Output from the 'grub-kbdcomp' command:" >&2
    printf '%s\n' "${grub_kbdcomp_output}" >&2
    return 1
  fi

  name_part_list=()
  for name_part in "${args[@]}"; do
    if [ -n "${name_part:-}" ]; then
      name_part_list+=( "${name_part}" )
    fi
  done
  (IFS='-'; printf '%s\n' "${name_part_list[*]}" | sponge -- "${grub_kb_layout_dir}/user-layout.name")

  if [ "${do_update_grub}" = 'true' ]; then
    rebuild_grub_config
  fi

  printf '%s\n' "${FUNCNAME[0]}: INFO: GRUB keymap configuration success."
}

build_all_grub_keymaps() {
  local keymap_list keymap old_keymap_file grub_kbdcomp_output \
    do_read_stdin

  do_read_stdin='false'

  while [ -n "${1:-}" ]; do
    case "$1" in
      '--help'|'-h')
        print_usage
        exit 0
        ;;
      '--read-stdin')
        do_read_stdin='true'
        shift
        ;;
      '--no-update-grub')
        do_update_grub='false'
        shift
        ;;
      *)
        printf '%s\n' "${FUNCNAME[0]}: ERROR: Unrecognized argument '$1'!"
        return 1
        ;;
    esac
  done

  if [ "${do_read_stdin}" = 'true' ]; then
    printf '%s\n' "${FUNCNAME[0]}: INFO: Getting list of keyboard layouts from 'stdin' (standard input)."
    readarray -t keymap_list
  else
    printf '%s\n' "${FUNCNAME[0]}: INFO: Getting list of available keyboard layouts from 'localectl-static'."
    readarray -t keymap_list <<< "${localectl_kb_layouts}"
  fi

  if ! mkdir --parents -- "${grub_kb_layout_dir}"; then
    printf '%s\n' "${FUNCNAME[0]}: ERROR: Cannot create GRUB keyboard layout dir '${grub_kb_layout_dir}'!" >&2
    return 1
  fi

  if ! command -v 'grub-kbdcomp' >/dev/null 2>&1; then
    printf '%s\n' "${FUNCNAME[0]}: ERROR: The 'grub-kbdcomp' program is unavailable in the PATH environment variable or not installed." >&2
    return 1
  fi

  printf '%s\n' "${FUNCNAME[0]}: INFO: Building keyboard layouts for GRUB."
  for old_keymap_file in "${grub_kb_layout_dir}/"* ; do
    if ! [ -f "${old_keymap_file}" ]; then
      continue
    fi
    if [ "${old_keymap_file}" = "${grub_kb_layout_dir}/user-layout.gkb" ] \
      || [ "${old_keymap_file}" = "${grub_kb_layout_dir}/user-layout.name" ]; then
      continue
    fi
    safe-rm -- "${old_keymap_file}"
  done
  for keymap in "${keymap_list[@]}"; do
    if [ "${keymap}" = 'custom' ]; then
      continue
    fi

    if ! grub_kbdcomp_output="$(
      grub-kbdcomp -o "${grub_kb_layout_dir}/${keymap}.gkb" "${keymap}" 2>&1
    )"; then
      printf '%s\n' "${FUNCNAME[0]}: WARNING: 'grub-kbdcomp' failed to build keyboard layout '${keymap}'!" >&2
      printf '%s\n' "${FUNCNAME[0]}: Output from command 'grub-kbdcomp -o ${grub_kb_layout_dir}/${keymap}.gkb ${keymap}':" >&2
      printf '%s\n' "${grub_kbdcomp_output}" >&2
    fi
  done

  if [ "${do_update_grub}" = 'true' ]; then
    rebuild_grub_config
  fi

  printf '%s\n' "${FUNCNAME[0]}: INFO: Done building keyboard layouts for GRUB."
}

interactive_ui_help_layout() {
  printf '%s\n' "\
Each keyboard layout supported by the system has a short, usually two-letter
code associated with it. The code generally corresponds to the nation the
layout is most commonly used in. Some common layouts, in alphabetical order:
- cz -> Czech (QWERTZ)
- de -> German (QWERTZ)
- es -> Spanish (QWERTY)
- us -> English (US QWERTY)

Multiple keyboard layouts may be specified at once if you intend to switch
between layouts frequently. Layouts must be comma-separated. A maximum of
four may be set at any one time.

For instance, to set US English, German, and Czech as the keyboard layouts,
specify 'us,de,cz'.
"
}

interactive_ui_help_variant() {
  printf '%s\n' "\
Each keyboard layout may optionally have a variant associated with it.
Variants are used to select alternate keyboard layouts for the same
language, such as Dvorak and Colemak. You should only use variants if you
know they are useful to you.

If you choose to specify keyboard layout variants, you must specify one
variant per layout chosen previously. Similar to layouts, variants must be
comma-separated. If you wish to skip setting the layout for a variant, omit
the variant from the list, but do not omit the comma that would have been
typed if you had specified a variant.

For instance, to set English (US Dvorak) and English (US Colemak) layouts,
specify 'us,us' as the keyboard layouts and 'dvorak,colemak' as the
variants. To set English (US QWERTY), English (US Dvorak), and German
(QWERTZ) layouts, specify 'us,us,de' as the keyboard layouts and ',dvorak,'
as the variants.
"
}

interactive_ui_help_option() {
  printf '%s\n' "\
A number of keyboard layout customizations may be applied using options.
Some common options:
- compose:ralt -> Sets the right Alt key as the Compose key, useful for
  typing accent marks and other characters not often typed with the chosen
  layout.
- grp:alt_shift_toggle -> Toggles between keyboard layouts any time
  Alt+Shift is pressed.
- caps:backspace -> Makes the Caps Lock key act as a second backspace key.

Multiple keyboard options may be specified at once. Options must be
comma-separated.

For instance, to set the right Alt key as the Compose key, and make
Alt+Shift the keyboard layout switch shortcut, specify
'compose:ralt,grp:alt_shift_toggle' as the keyboard layout options.
"
}

interactive_ui() {
  local kb_set_func kb_set_opts layout_str variant_str option_str \
    variant_key_str

  skl_interactive='true'
  kb_set_func="${1:-}"
  if [ -z "${kb_set_func}" ]; then
    printf '%s\n' "${FUNCNAME[0]}: ERROR: No keyboard layout set function provided!" >&2
    return 1
  fi
  shift
  kb_set_opts=()
  while [ -n "${1:-}" ]; do
    case "$1" in
      --)
        break
        ;;
      -*)
        kb_set_opts+=( "$1" )
        shift
        ;;
      *)
        break
        ;;
    esac
  done

  printf '%s\n' "\
Type 'list' at any prompt to see a list of valid options.
If the list is longer than will fit on the screen, use arrow keys to scroll.
Press 'q' to exit the scrollable list.

Type 'help' for help.

Type 'exit' to quit without changing keyboard layout settings.
"

  while true; do
    read -r -p 'Enter the keyboard layout(s) you would like to use: ' -- layout_str
    printf '\n'
    if [ -z "${layout_str}" ]; then
      printf '%s\n' 'No keyboard layouts specified. Exiting.'
      return 0
    fi
    ## Normalize the layout string so it is all lowercase and has no spaces in
    ## it. This way whether the user specifies "us,de" or "us, de" or 'US, DE'
    ## or even "U   s,de     ,    eS", it works. No XKB keyboard layouts
    ## contain spaces or capital letters.
    layout_str="$(tr -d ' ' <<< "${layout_str,,}")"
    if [ "${layout_str}" = 'list' ]; then
      ## Sanity test.
      "${timeout_command[@]}" localectl-static --no-pager list-x11-keymap-layouts >/dev/null
      ## Use without '--no-pager' for user output.
      ## Cannot use 'timeout'.
      ## 'timeout' is not compatible with the pager and '--no-pager' is unwanted.
      #"${timeout_command[@]}" localectl --no-pager list-x11-keymap-layouts
      localectl-static list-x11-keymap-layouts
      ## TODO: Minor. Replace above using 'pager' or similar?
      #printf '%s\n' "${localectl_kb_layouts}" | pager
      ##       localectl's default pager is better. It does not clear output of this script.
      continue
    fi
    if [ "${layout_str}" = 'help' ]; then
      interactive_ui_help_layout
      continue
    fi
    if [ "${layout_str}" = 'exit' ]; then
      printf '%s\n' "${FUNCNAME[0]}: INFO: Exiting without setting keyboard layout."
      return 0
    fi
    if check_keyboard_layouts "${layout_str}"; then
      break
    fi
  done

  while true; do
    read -r -p 'Enter the keyboard layout variant(s) if desired, leave empty otherwise: ' -- variant_str
    printf '\n'
    if [ -z "${variant_str}" ]; then
      break
    fi
    ## Normalize the variant string similar to how we normalize the layout
    ## string. Unfortunately, some variants like "UnicodeExpert" contain
    ## capitals, so we can't normalize everything to lowercase.
    variant_str="$(tr -d ' ' <<< "${variant_str}")"
    if [ "${variant_str,,}" = 'list' ]; then
      if ! grep --quiet ',' <<< "${layout_str}"; then
        "${timeout_command[@]}" localectl-static --no-pager list-x11-keymap-variants "${layout_str}"
      else
        read -r -p 'Enter the keyboard layout to view variants for: ' -- variant_key_str
        variant_key_str="$(tr -d ' ' <<< "${variant_key_str,,}")"
        if grep -q ',' <<< "${variant_key_str}" ; then
          printf '%s\n' "${FUNCNAME[0]}: ERROR: Only one layout may be specified to view the variants of!" >&2
          continue
        fi
        if ! [[ "${layout_str}" =~ (^|,)"${variant_key_str}"(,|$) ]]; then
          printf '%s\n' "${FUNCNAME[0]}: ERROR: Specified layout is not in the previously specified layout list!" >&2
          continue
        fi
        "${timeout_command[@]}" localectl-static --no-pager list-x11-keymap-variants "${variant_key_str}"
      fi
      continue
    fi
    if [ "${variant_str,,}" = 'help' ]; then
      interactive_ui_help_variant
      continue
    fi
    if [ "${variant_str}" = 'exit' ]; then
      printf '%s\n' "${FUNCNAME[0]}: INFO: Exiting without setting keyboard layout."
      return 0
    fi
    if check_keyboard_layout_variants "${layout_str}" "${variant_str}"; then
      break
    fi
  done

  while true; do
    read -r -p 'Enter the keyboard layout option(s) if desired, leave empty otherwise: ' -- option_str
    printf '\n'
    if [ -z "${option_str}" ]; then
      break
    fi
    ## More normalizing, again we can't normalize everything to lowercase
    ## because some options like "eurosign:E" contain capital letters.
    option_str="$(tr -d ' ' <<< "${option_str}")"
    if [ "${option_str,,}" = 'list' ]; then
      ## Sanity test.
      "${timeout_command[@]}" localectl-static --no-pager list-x11-keymap-options >/dev/null
      ## Run without '--no-pager' for user output.
      localectl-static list-x11-keymap-options
      continue
    fi
    if [ "${option_str,,}" = 'help' ]; then
      interactive_ui_help_option
      continue
    fi
    if [ "${option_str}" = 'exit' ]; then
      printf '%s\n' "${FUNCNAME[0]}: INFO: Exiting without setting keyboard layout."
      return 0
    fi
    if check_keyboard_layout_options "${option_str}"; then
      break
    fi
  done

  "${kb_set_func}" \
    "${kb_set_opts[@]}" \
    "${layout_str}" \
    "${variant_str}" \
    "${option_str}" \
    || return 1
}

parse_cmd() {
  while [ -n "${1:-}" ]; do
    case "$1" in
      '--no-persist')
        do_persist='false'
        shift
        ;;
      '--help'|'-h')
        print_usage
        exit 0
        ;;
      '--no-reload')
        no_reload='true'
        shift
        ;;
      '--config='*)
        labwc_config_path="$(cut -d'=' -f2- <<< "$1")"
        if [ -z "$labwc_config_path" ]; then
          printf '%s\n' "${FUNCNAME[0]}: ERROR: No '--config=path' specified!" >&2
          return 1
        fi
        shift
        ;;
      '--interactive')
        skl_interactive='true'
        shift
        ;;
      '--no-update-grub')
        do_update_grub='false'
        shift
        ;;
      '--build-all')
        ## TODO
        shift
        ;;
      '--')
        shift
        break
        ;;
      *)
        break
        ;;
    esac
  done

  args=( "$@" )
  true "${FUNCNAME[0]}: args: ${args[*]}"
}

## Debugging.
#ischroot() {
#   true
#}

printf '%s\n' "$0: Start."
printf '%s\n' ""

command -v safe-rm >/dev/null
command -v mktemp >/dev/null
command -v mv >/dev/null
command -v dirname >/dev/null
command -v mkdir >/dev/null
command -v overwrite >/dev/null
command -v stcat >/dev/null
command -v sponge >/dev/null
command -v timeout >/dev/null
command -v ischroot >/dev/null
command -v jq >/dev/null
command -v tr >/dev/null
command -v loginctl >/dev/null
command -v /usr/libexec/helper-scripts/query-sock-pid >/dev/null
command -v localectl-static >/dev/null

timeout_command=("timeout" "--kill-after" "5" "5")

skl_xkb_env_var_names=(
  'XKB_DEFAULT_LAYOUT'
  'XKB_DEFAULT_VARIANT'
  'XKB_DEFAULT_OPTIONS'
)
skl_default_keyboard_var_names=(
  'XKBLAYOUT'
  'XKBVARIANT'
  'XKBOPTIONS'
)

args=""
skl_interactive='false'
do_update_grub='true'
do_persist='true'
no_reload='false'

[[ -v "HOME" ]] || HOME="/home/user"
labwc_config_path="${HOME}/.config/labwc/environment"

grub_kb_layout_dir='/boot/grub/kb_layouts'

localectl_kb_layouts="$("${timeout_command[@]}" localectl-static --no-pager list-x11-keymap-layouts)"

parse_cmd "$@"
