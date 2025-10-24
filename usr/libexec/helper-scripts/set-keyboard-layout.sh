#!/bin/bash

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  set -o errexit
  set -o nounset
  set -o errtrace
  #  set -o pipefail
fi

command -v safe-rm >/dev/null
command -v localectl >/dev/null
command -v mktemp >/dev/null
command -v mv >/dev/null
command -v dirname >/dev/null
command -v mkdir >/dev/null
command -v overwrite >/dev/null
command -v stcat >/dev/null

skl_interactive='false'
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

error_handler() {
  exit_code="${?}"
  printf '%s\n' "\
BASH_COMMAND: ${BASH_COMMAND}
exit_code: ${exit_code}"
  exit "${exit_code}"
}

## Checks to see if all items in "check_str" are present in the output of a
## command that lists valid items.
is_layout_data_valid() {
  local valid_list_cmd check_str check_list check_item valid_item_list \
    valid_item is_item_valid

  check_str="${1:-}"
  shift
  valid_list_cmd=( "$@" )
  if [ "${#valid_list_cmd[@]}" = '0' ] || [ -z "${valid_list_cmd[0]}" ]; then\
    return 1
  fi
  if [ -z "${check_str}" ]; then return 1; fi

  readarray -t check_list < <(printf '%s\n' "${check_str}" | tr ',' '\n')
  readarray -t valid_item_list < <("${valid_list_cmd[@]}")

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
    printf '%s\n' "$0: ERROR: Empty keyboard layout string provided!" >&2
    return 1
  fi
  readarray -t layout_arr < <(printf '%s\n' "${layout_str}" | tr ',' '\n')
  for layout in "${layout_arr[@]}"; do
    if [ -z "${layout}" ]; then
      printf '%s\n' "$0: ERROR: Empty element found in keyboard layouts!" >&2
      return 1
    fi
  done

  ## Ensure the user has no more than four keyboard layouts specified (this
  ## is the maximum number supported by XKB under X11 according to
  ## https://www.x.org/archive/X11R7.5/doc/input/XKB-Config.html, and it is
  ## the maximum number labwc appears to support).
  readarray -t kb_layout_list < <(printf '%s\n' "${layout_str}" | tr ',' '\n')
  if (( ${#kb_layout_list[@]} > 4 )); then
    printf '%s\n' "$0: ERROR: Too many keyboard layouts specified, must specify 4 or less!" >&2
    return 1
  fi

  ## Ensure the specified keyboard layout(s) are valid.
  if ! is_layout_data_valid "${layout_str}" \
    localectl list-x11-keymap-layouts ; then
    printf '%s\n' "$0: ERROR: Specified keyboard layout(s) are not all valid!" >&2
    if [ "${skl_interactive}" = 'false' ]; then
      printf '%s\n' "$0: INFO: Run 'localectl list-x11-keymap-layouts' to get a list of valid layouts." >&2
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
    printf '%s\n' "$0: ERROR: Empty keyboard layout string provided!" >&2
    return 1
  fi
  if [ -z "${variant_str}" ]; then
    printf '%s\n' "$0: ERROR: Empty keyboard layout variant string provided!" >&2
    return 1
  fi

  readarray -t kb_layout_list < <(printf '%s\n' "${layout_str}" | tr ',' '\n')
  ## Don't redo the keyboard layout count check, that's been done by
  ## check_keyboard_layouts already
  readarray -t kb_variant_list < <(printf '%s\n' "${variant_str}" | tr ',' '\n')

  if (( ${#kb_layout_list[@]} < ${#kb_variant_list[@]} )); then
    printf '%s\n' "$0: ERROR: Insufficient number of keyboard layouts specified for number of variants!" >&2
    return 1
  fi

  if (( ${#kb_layout_list[@]} > ${#kb_variant_list[@]} )); then
    printf '%s\n' "$0: ERROR: Too many keyboard layouts specified for number of variants!" >&2
    return 1
  fi

  for kb_idx in "${!kb_layout_list[@]}"; do
    if [ -z "${kb_variant_list[kb_idx]}" ]; then continue; fi
    if ! is_layout_data_valid "${kb_variant_list[kb_idx]}" \
      localectl list-x11-keymap-variants "${kb_layout_list[kb_idx]}" ; then
      printf '%s\n' "$0: ERROR: Specified keyboard layout variant '${kb_variant_list[kb_idx]}' for layout '${kb_layout_list[kb_idx]}' is not valid!" >&2
      if [ "${skl_interactive}" = 'false' ]; then
        printf '%s\n' "$0: INFO: Run 'localectl list-x11-keymap-variants ${kb_layout_list[kb_idx]}' to get a list of valid layout variants for the '${kb_layout_list[kb_idx]}' layout." >&2
      fi
      return 1
    fi
  done
}

check_keyboard_layout_options() {
  local option_str option_arr option

  option_str="${1:-}"
  if [ -z "${option_str}" ]; then
    printf '%s\n' "$0: ERROR: Empty keyboard layout options string provided!" >&2
    return 1
  fi
  readarray -t option_arr < <(printf '%s\n' "${option_str}" | tr ',' '\n')
  for option in "${option_arr[@]}"; do
    if [ -z "${option}" ]; then
      printf '%s\n' "$0: ERROR: Empty element found in keyboard layout options!" >&2
      return 1
    fi
  done

  if ! is_layout_data_valid "${option_str}" \
    localectl list-x11-keymap-options ; then
    printf '%s\n' "$0: ERROR: Specified keyboard layout option(s) are not valid!" >&2
    if [ "${skl_interactive}" = 'false' ]; then
      printf '%s\n' "$0: INFO: Run 'localectl list-x11-keymap-options' to get a list of valid layout options." >&2
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
    printf '%s\n' "$0: ERROR: No new variables provided!" >&2
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

## Sets the XKB layout(s), variant(s), and option(s) in labwc, either for just
## this session or persistently.
set_labwc_keymap() {
  local labwc_config_bak_path var_idx args labwc_env_file_string \
    labwc_config_directory do_persist no_reload labwc_config_path \
    calc_replace_args labwc_existing_config

  ## Parse command line arguments
  do_persist='false'
  no_reload='false'
  labwc_config_path="${HOME}/.config/labwc/environment"
  labwc_config_bak_path=''
  while [ -n "${1:-}" ]; do
    case "${1:-}" in
    '--persist')
      do_persist='true'
      shift
      ;;
    '--help'|'-h')
      print_usage
      return 0
      ;;
    '--no-reload')
      no_reload='true'
      shift
      ;;
    '--config')
      if [ -z "${2:-}" ]; then
        printf '%s\n' "$0: ERROR: No config path specified!" >&2
        return 1
      fi
      labwc_config_path="${2:-}"
      shift 2
      ;;
    '--interactive')
      skl_interactive='true'
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

  ## We must have at least one, but no more than three, arguments specifying the
  ## keyboard layout(s).
  if [ "${#args[@]}" = '0' ] || [ -z "${args[0]:-}" ] \
    || (( ${#args[@]} > 3 )); then
    ## The print_usage function is provided by the script that sources this
    ## library.
    print_usage
    return 1
  fi

  ## If we have less than three arguments, populate the `args` array with empty
  ## strings for the remaining arguments. This will make labwc unset the
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
    printf '%s\n' "$0: ERROR: --config '${labwc_config_path}' is a folder but should be a file!" >&2
    return 1
  fi

  labwc_config_directory="$(dirname -- "${labwc_config_path}")"

  ## Ensure the labwc configuration directory exists.
  if ! mkdir --parents -- "${labwc_config_directory}" ; then
    printf '%s\n' "$0: ERROR: Cannot create labwc config directory '${labwc_config_directory}'!" >&2
    return 1
  fi

  ## If labwc's environment config file exists, read it.
  labwc_existing_config=''
  if [ -f "${labwc_config_path}" ]; then
    if ! [ -r "${labwc_config_path}" ]; then
      printf '%s\n' "$0: ERROR: No read permissions on labwc environment config '${labwc_config_path}'!" >&2
      return 1
    fi

    if ! labwc_existing_config="$(cat -- "${labwc_config_path}")" ; then
      printf '%s\n' "$0: ERROR: Cannot read existing labwc environment config '${labwc_config_path}'!" >&2
      return 1
    fi

    ## If we do not want the new configuration to be persistent, move the
    ## existing configuration to a temporary backup location.
    if [ "${do_persist}" = 'false' ]; then
      labwc_config_bak_path="$(mktemp)"
      if ! mv -- "${labwc_config_path}" "${labwc_config_bak_path}" ; then
        printf '%s\n' "$0: ERROR: Cannot move existing labwc environment config '${labwc_config_path}' to backup location '${labwc_config_bak_path}'!" >&2
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

  ## Write the new config file contents and load them into labwc.
  if ! overwrite "${labwc_config_path}" "${labwc_env_file_string}" >/dev/null ; then
    printf '%s\n' "$0: ERROR: Cannot write new labwc environment config '${labwc_config_path}'!" >&2
    return 1
  fi

  if [ "${no_reload}" = 'false' ]; then
    if ! command -v labwc >/dev/null; then
      printf '%s\n' "$0: WARNING: 'labwc' not available in PATH or not installed." >&2
    else
      if labwc --reconfigure; then
        printf '%s\n' "$0: INFO: 'labwc --reconfigure' OK." >&2
      else
        printf '%s\n' "$0: WARNING: 'labwc --reconfigure' reconfiguration failed!" >&2
      fi
    fi
  fi

  ## If we do not want to persist the new configuration, put the old
  ## configuration back (or just delete the new config file if there wasn't an
  ## old config file).
  if [ -n "${labwc_config_bak_path}" ]; then
    printf '%s\n' "$0: INFO: ephemeral '${labwc_config_path}' contents:" >&2
    stcat "${labwc_config_path}" >&2
    if ! mv -- "${labwc_config_bak_path}" "${labwc_config_path}" ; then
      printf '%s\n' "$0: ERROR: Cannot move backup labwc environment config '${labwc_config_bak_path}' to original location '${labwc_config_path}'!" >&2
      return 1
    fi
  elif [ "${do_persist}" = 'true' ]; then
    printf '%s\n' "$0: INFO: new '${labwc_config_path}' contents:" >&2
    stcat "${labwc_config_path}" >&2
  elif [ "${do_persist}" = 'false' ]; then
    if ! safe-rm -- "${labwc_config_path}" ; then
      printf '%s\n' "$0: ERROR: Cannot remove temporary labwc environment config '${labwc_config_path}'!" >&2
      return 1
    fi
  fi
}

dpkg_reconfigure_function() {
  local dpkg_reconfigure_output
  printf '%s\n' "$0: EXECUTING: '${*}'" >&2
  dpkg_reconfigure_output="$("${@}" 2>&1)"
  ## dpkg-reconfigure can cause the following error message:
  #cat: '/sys/bus/usb/devices/*:*/bInterfaceClass': No such file or directory
  #cat: '/sys/bus/usb/devices/*:*/bInterfaceSubClass': No such file or directory
  #cat: '/sys/bus/usb/devices/*:*/bInterfaceProtocol': No such file or directory
  printf '%s\n' "${dpkg_reconfigure_output}" | grep --invert-match --fixed-strings -- "cat: '/sys/bus/usb/devices/*:*/"
}

## Sets the XKB layout(s), variant(s), and option(s) for the entire system.
## NOTE: Changes will take effect after a reboot. This is because CLI keyboard
## layout changes would need to be applied with setupcon, but setupcon may not
## be safe to use to apply CLI keyboard layout changes while a graphical
## session is active. Quoting the manpage for setupcon:
##
##   --force
##     Do not check whether we are on the console. Notice that you can be
##     forced to hard-reboot your computer if you run setupcon with this
##     option and the screen is controlled by a X server.
set_system_keymap() {
  local args var_idx kb_conf_file_string kb_conf_path kb_conf_dir \
    calc_replace_args labwc_system_wide_config_path \
    labwc_system_wide_config_dir labwc_greeter_config_path \
    labwc_greeter_config_dir dpkg_reconfigure_command

  ## Parse command line arguments
  kb_conf_dir='/etc/default'
  kb_conf_path="${kb_conf_dir}/keyboard"
  labwc_system_wide_config_dir='/etc/xdg/labwc'
  labwc_system_wide_config_path="${labwc_system_wide_config_dir}/environment"
  labwc_greeter_config_dir='/etc/greetd/labwc-config'
  labwc_greeter_config_path="${labwc_greeter_config_dir}/environment"
  while [ -n "${1:-}" ]; do
    case "${1:-}" in
      '--help')
        print_usage
        return 0
        ;;
      '--interactive')
        skl_interactive='true'
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

  ## We must have at least one, but no more than three, arguments specifying the
  ## keyboard layout(s).
  if [ "${#args[@]}" = '0' ] || [ -z "${args[0]:-}" ] \
    || (( ${#args[@]} > 3 )); then
    ## The print_usage function is provided by the script that sources this
    ## library.
    print_usage
    return 1
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
    printf '%s\n' "$0: ERROR: Cannot ensure the existence of '${kb_conf_dir}'!" >&2
    return 1
  fi
  if ! mkdir --parents -- "${labwc_system_wide_config_dir}" ; then
    printf '%s\n' "$0: ERROR: Cannot ensure the existence of '${labwc_system_wide_config_dir}'!" >&2
    return 1
  fi
  if ! mkdir --parents -- "${labwc_greeter_config_dir}" ; then
    printf '%s\n' "$0: ERROR: Cannot ensure the existence of '${labwc_greeter_config_dir}'!" >&2
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
    printf '%s\n' "$0: ERROR: Cannot write new keyboard config file '${kb_conf_path}'!" >&2
    return 1
  fi

  printf '%s\n' "$0: INFO: new '${kb_conf_path}' contents:" >&2
  stcat "${kb_conf_path}" >&2

  dpkg_reconfigure_command=( "dpkg-reconfigure" "--frontend=noninteractive" "keyboard-configuration" )
  ## Test error handling.
  #dpkg_reconfigure_command=( "dpkg-reconfigure" )
  ## Apply the changes to the config file to the system.
  dpkg_reconfigure_function "${dpkg_reconfigure_command[@]}"

  ## Set the specified keyboard layout for labwc both system-wide and for the
  ## greeter.
  set_labwc_keymap \
    --persist \
    --no-reload \
    --config \
    "${labwc_system_wide_config_path}" \
    "${args[@]}" \
    || return 1
  set_labwc_keymap \
    --persist \
    --no-reload \
    --config \
    "${labwc_greeter_config_path}" \
    "${args[@]}" \
    || return 1
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
" >&2
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
" >&2
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
" >&2
}

interactive_ui() {
  local kb_set_func kb_set_opts layout_str variant_str option_str \
    variant_key_str

  skl_interactive='true'
  kb_set_func="${1:-}"
  if [ -z "${kb_set_func}" ]; then
    printf '%s\n' "$0: ERROR: No keyboard layout set function provided!"
    return 1
  fi
  shift
  kb_set_opts=( "$@" )

  printf '%s\n' "\
Type 'list' at any prompt to see a list of valid options.
If the list is longer than will fit on the screen, use arrow keys to scroll.
Press 'q' to exit the scrollable list.

Type 'help' for help.

Type 'exit' to quit without changing keyboard layout settings.
" >&2

  while true; do
    read -r -p 'Enter the keyboard layout(s) you would like to use: ' -- layout_str
    printf '\n' >&2
    if [ -z "${layout_str}" ]; then
      printf '%s\n' 'No keyboard layouts specified. Exiting.' >&2
      return 0
    fi
    ## Normalize the layout string so it is all lowercase and has no spaces in
    ## it. This way whether the user specifies "us,de" or "us, de" or 'US, DE'
    ## or even "U   s,de     ,    eS", it works. No XKB keyboard layouts
    ## contain spaces or capital letters.
    layout_str="$(tr -d ' ' <<< "${layout_str,,}")"
    if [ "${layout_str}" = 'list' ]; then
      localectl list-x11-keymap-layouts
      continue
    fi
    if [ "${layout_str}" = 'help' ]; then
      interactive_ui_help_layout
      continue
    fi
    if [ "${layout_str}" = 'exit' ]; then
      printf '%s\n' "$0: INFO: Exiting without setting keyboard layout." >&2
      return 0
    fi
    if check_keyboard_layouts "${layout_str}"; then
      break
    fi
  done

  while true; do
    read -r -p 'Enter the keyboard layout variant(s) if desired, leave empty otherwise: ' -- variant_str
    printf '\n' >&2
    if [ -z "${variant_str}" ]; then
      break
    fi
    ## Normalize the variant string similar to how we normalize the layout
    ## string. Unfortunately, some variants like "UnicodeExpert" contain
    ## capitals, so we can't normalize everything to lowercase.
    variant_str="$(tr -d ' ' <<< "${variant_str}")"
    if [ "${variant_str,,}" = 'list' ]; then
      if ! grep -q ',' <<< "${layout_str}"; then
        localectl list-x11-keymap-variants "${layout_str}"
      else
        read -r -p 'Enter the keyboard layout to view variants for: ' -- variant_key_str
        variant_key_str="$(tr -d ' ' <<< "${variant_key_str,,}")"
        if grep -q ',' <<< "${variant_key_str}" ; then
          printf '%s\n' "$0: ERROR: Only one layout may be specified to view the variants of!" >&2
          continue
        fi
        if ! [[ "${layout_str}" =~ (^|,)"${variant_key_str}"(,|$) ]]; then
          printf '%s\n' "$0: ERROR: Specified layout is not in the previously specified layout list!" >&2
          continue
        fi
        localectl list-x11-keymap-variants "${variant_key_str}"
      fi
      continue
    fi
    if [ "${variant_str,,}" = 'help' ]; then
      interactive_ui_help_variant
      continue
    fi
    if [ "${variant_str}" = 'exit' ]; then
      printf '%s\n' "$0: INFO: Exiting without setting keyboard layout." >&2
      return 0
    fi
    if check_keyboard_layout_variants "${layout_str}" "${variant_str}"; then
      break
    fi
  done

  while true; do
    read -r -p 'Enter the keyboard layout option(s) if desired, leave empty otherwise: ' -- option_str
    printf '\n' >&2
    if [ -z "${option_str}" ]; then
      break
    fi
    ## More normalizing, again we can't normalize everything to lowercase
    ## because some options like "eurosign:E" contain capital letters.
    option_str="$(tr -d ' ' <<< "${option_str}")"
    if [ "${option_str,,}" = 'list' ]; then
      localectl list-x11-keymap-options
      continue
    fi
    if [ "${option_str,,}" = 'help' ]; then
      interactive_ui_help_option
      continue
    fi
    if [ "${option_str}" = 'exit' ]; then
      printf '%s\n' "$0: INFO: Exiting without setting keyboard layout." >&2
      return 0
    fi
    if check_keyboard_layout_options "${option_str}"; then
      break
    fi
  done

  "${kb_set_func}" \
    --interactive \
    "${kb_set_opts[@]}" \
    "${layout_str}" \
    "${variant_str}" \
    "${option_str}" \
    || return 1
  printf '%s\n' "$0: INFO: Keyboard layout change successful." >&2
}
