#!/bin/bash

## Copyright (C) 2025 - 2025 Benjamin Grande M. S. <ben.grande.b@gmail.com>
## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## style-ok: no-strict -- sourced library; a top-level strict-mode block
## would leak 'set -o errexit'/'nounset' into the sourcing shell.

## https://www.kicksecure.com/wiki/User#Meanings_of_Special_Characters_in_the_Password_Field_of_/etc/shadow_File
##
## Changing account state on Unix systems is not standardize and different
## tools leads to different results and sometimes pitfalls.
##
## This is a wrapper around common Unix utilities to affirm account state
## independent if the account already exists or has a password set or not
## as well as query fields from user and group databases.
##
## When modifying a password, encryption is skipped with 'chpasswd -c NONE' to
## not modify an already encrypted or plain text password and to be able to
## provide symbols.

source "${HELPER_SCRIPTS_PATH:-}"/usr/libexec/helper-scripts/has.bsh
source "${HELPER_SCRIPTS_PATH:-}"/usr/libexec/helper-scripts/as_root.sh
source "${HELPER_SCRIPTS_PATH:-}"/usr/libexec/helper-scripts/log_run_die.sh


## ----------------------- ##
## Usage of account_state.sh
##
##  ## Assign user and check if it exists (use OR if errexit is disabled).
##  user="user"
##  is_user "${user}" || exit 1
##  ## Do wanted actions.
##  unlock_pass "${user}"
## ----------------------- ##


## Description: Check is user or group name is valid.
## Output: None
## Return: 1 if name is invalid
## Usage: is_name_valid NAME
## Example: is_name_valid NAME
is_name_valid(){
  log info "${FUNCNAME[0]} $*"
  ## LC_ALL=C makes the [a-zA-Z] ranges ASCII-only.
  local name LC_ALL=C
  name="${1:-}"
  ## Syntax based on /etc/adduser.conf SYS_NAME_REGEX plus dot and at sign.
  ## (SYS_NAME_REGEX is a strict superset of NAME_REGEX.) Avoids parsing bugs
  ## in other applications.
  if [[ ! ${name} =~ ^[a-zA-Z_][a-zA-Z0-9_.@-]*\$?$ ]]; then
    log error "Invalid name: '${name}'"
    return 1
  fi
}


## Description: Escape name to be used by in RegEx
## Output: Escaped name
## Return: None
## Usage: escape_name NAME
## Example: escape_name NAME
escape_name(){
  log info "${FUNCNAME[0]} $*"
  local name
  name="${1:-}"
  name="${name//./\\.}"
  name="${name//$/\\$}"
  printf '%s' "${name}"
}


## Description: Check if user exists.
## Output: None
## Return: 1 if user does not exist.
## Usage: is_user USER
## Example: is_user user
is_user(){
  has getent || return 1
  log info "${FUNCNAME[0]} $*"
  ## Avoid running functions twice.
  if test "${FUNCNAME[1]:-}" != "get_pass"; then
    as_root
  fi
  local user
  user="${1:-}"
  if test -z "${user}"; then
    log error "No user provided"
    return 1
  fi
  is_name_valid "${user}" || return 1
  if getent passwd -- "${user}" >/dev/null 2>&1; then
    return 0
  fi
  log error "User does not exist: '${user}'"
  return 1
}


## Description: Check if group exists.
## Output: None
## Return: 1 if group does not exist.
## Usage: is_group GROUP
## Example: is_group root
is_group(){
  has getent || return 1
  log info "${FUNCNAME[0]} $*"
  local group group_escaped
  group="${1:-}"
  if test -z "${group}"; then
    log error "No group provided"
    return 1
  fi
  is_name_valid "${group}" || return 1
  if getent group -- "${group}" >/dev/null 2>&1; then
    return 0
  fi
  log error "Group does not exist: '${group}'"
  return 1
}


## Description: Check whether a non-root account belongs to a group.
## Output: None
## Return: 0 if account exists, 1 otherwise.
## Usage: group_has_nonroot_member GROUP
## Example: group_has_nonroot_member sudo
group_has_nonroot_member() {
  has getent || return 1
  log info "${FUNCNAME[0]} $*"
  local group group_gid member_list_str member entry_name entry_gid
  local -a member_list
  group="${1:-}"
  if test -z "${group}"; then
    log error "No group provided"
    return 1
  fi
  is_name_valid "${group}" || return 1
  group_gid="$(getent group -- "${group}" 2>/dev/null | cut -d: -f3)" || true
  [ -n "${group_gid}" ] || return 1

  ## REMINDER: Accounts other than "root" with UID 0 are intentionally
  ## unsupported.

  ## Check user primary GIDs
  while IFS=":" read -r entry_name _ _ entry_gid _; do
    if [ "${entry_gid}" = "${group_gid}" ] && [ "${entry_name}" != "root" ]; then
      return 0
    fi
  done < <(getent passwd)

  ## Check supplementary members
  member_list_str="$(getent group -- "${group}" 2>/dev/null | cut -d: -f4)" || true
  IFS="," read -r -a member_list <<< "${member_list_str}" || true
  for member in "${member_list[@]}"; do
    if [ -n "${member}" ] && [ "${member}" != "root" ]; then
      return 0
    fi
  done
  return 1
}


## Description: Get user password.
## Output: Password field.
## Usage: get_pass USER
## Example: get_pass user
get_pass(){
  has getent || return 1
  log info "${FUNCNAME[0]} $*"
  as_root
  local user pass user_escaped
  user="${1:-}"
  is_user "${user}" || return 1
  pass="$(get_entry "${user}" shadow pass)" || return 1
  printf '%s' "${pass}"
}


## Description: Get password without its state.
## Output: Password prefix is trimmed.
## Usage: get_clean_pass USER PREFIX
## Example: get_clean_pass user '!*'
## Note that the prefix is used as part of a regex bracket expression,
## therefore any brackets in it must be escaped and any dash if present must
## be the first or last character.
get_clean_pass(){
  log info "${FUNCNAME[0]} $*"
  local user pass symbol
  user="${1:-}"
  is_user "${user}" || return 1
  symbol="${2:-"!*"}"
  pass="$(get_pass "${user}")" || return 1
  [[ "${pass}" =~ ^[${symbol}]*(.*)$ ]] || return 1
  pass="${BASH_REMATCH[1]}"
  printf '%s\n' "${pass}"
}


## Description: Check if password is empty.
## Output: None
## Return: 0 when empty, 1 otherwise.
## Usage: is_pass_empty USER
## Example: is_pass_empty user
is_pass_empty(){
  log info "${FUNCNAME[0]} $*"
  local user trim_pass
  user="${1:-}"
  is_user "${user}" || return 1
  trim_pass="$(get_clean_pass "${user}" '!*')" || return 1
  if test -z "${trim_pass}"; then
    return 0
  fi
  return 1
}


## Description: Check if password is locked.
## Output: None
## Return: 0 when locked, 1 otherwise.
## Usage: is_pass_locked USER
## Example: is_pass_locked user
is_pass_locked(){
  log info "${FUNCNAME[0]} $*"
  local user pass
  user="${1:-}"
  is_user "${user}" || return 1
  pass="$(get_pass "${user}")" || return 1
  case "${pass}" in
    "!"*)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}


## Description: Check if password is disabled.
## Output: None
## Return: 0 when disabled, 1 otherwise.
## Usage: is_pass_disabled USER
## Example: is_pass_disabled user
is_pass_disabled(){
  log info "${FUNCNAME[0]} $*"
  local user pass
  user="${1:-}"
  is_user "${user}" || return 1
  pass="$(get_pass "${user}")"
  case "${pass}" in
    "*"*|"!*"*)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}


## Description: Lock a password.
## Output: None
## Return: passwd
## Usage: lock_pass USER
## Example: lock_pass user
lock_pass(){
  log info "${FUNCNAME[0]} $*"
  has passwd || return 1
  local user
  user="${1:-}"
  is_user "${user}" || return 1
  if is_pass_locked "${user}"; then
    return 0
  fi
  passwd --quiet --lock -- "${user}"
}


## Description: Unlock a password.
## Output: None
## Return: chpasswd
## Usage: unlock_pass USER
## Example: unlock_pass user
unlock_pass(){
  log info "${FUNCNAME[0]} $*"
  has chpasswd || return 1
  local user pass
  user="${1:-}"
  is_user "${user}" || return 1
  if ! is_pass_locked "${user}"; then
    return 0
  fi
  ## The tools "passwd" and "usermod" can't unlock when password is empty.
  pass="$(get_clean_pass "${user}" '!')" || return 1
  chpasswd --crypt-method NONE <<< "${user}:${pass}"
}


## Description: Disable a password.
## Output: None
## Return: chpasswd
## Usage: disable_pass USER
## Example: disable_pass user
disable_pass(){
  log info "${FUNCNAME[0]} $*"
  has chpasswd || return 1
  local user pass
  user="${1:-}"
  is_user "${user}" || return 1
  if is_pass_disabled "${user}"; then
    return 0
  fi
  pass="$(get_clean_pass "${user}")" || return 1
  if is_pass_locked "${user}"; then
    chpasswd --crypt-method NONE <<< "${user}:!*${pass}" || return "$?"
    return 0
  fi
  chpasswd --crypt-method NONE <<< "${user}:*${pass}"
}


## Description: Enable a password.
## Output: None
## Return: chpasswd
## Usage: enable_pass USER
## Example: enable_pass user
enable_pass(){
  log info "${FUNCNAME[0]} $*"
  has chpasswd || return 1
  local user pass
  user="${1:-}"
  is_user "${user}" || return 1
  if ! is_pass_disabled "${user}"; then
    return 0
  fi
  if is_pass_locked "${user}"; then
    pass="$(get_clean_pass "${user}" '!*')" || return 1
    chpasswd --crypt-method NONE <<< "${user}:!${pass}" || return "$?"
    return 0
  fi
  pass="$(get_clean_pass "${user}" '*')" || return 1
  chpasswd --crypt-method NONE <<< "${user}:${pass}"
}


## Description: Transform field name to index per database
## Output: Field 0-indexed
## Return: Exit 1 if entry does not exist
## Usage: get_field DB FIELD
## Example: get_field passwd pass
get_field(){
  log info "${FUNCNAME[0]} $*"
  local db field index
  db="${1:-}"
  field="${2:-}"
  index=""
  case "${db}" in
    passwd)
      case "${field}" in
        pass)
          index=2
          ;;
        uid)
          index=3
          ;;
        gid)
          index=4
          ;;
        comment)
          index=5
          ;;
        home)
          index=6
          ;;
        shell)
          index=7
          ;;
      esac
      ;;
    shadow)
      case "${field}" in
        pass)
          index=2
          ;;
        last-pass-change)
          index=3
          ;;
        min-pass-age)
          index=4
          ;;
        max-pass-age)
          index=5
          ;;
        warn-pass-period)
          index=6
          ;;
        lock-pass-period)
          index=7
          ;;
        expiration-date)
          index=8
          ;;
      esac
      ;;
    group)
      case "${field}" in
        pass)
          index=2
          ;;
        gid)
          index=3
          ;;
        members)
          index=4
          ;;
      esac
      ;;
    gshadow)
      case "${field}" in
        pass)
          index=2
          ;;
        admins)
          index=3
          ;;
        members)
          index=4
          ;;
      esac
      ;;
    "")
      log error "No database provided"
      return 1
      ;;
    *)
      log error "Unsupported database: '${db}'"
      return 1
      ;;
  esac
  if test -z "${field}"; then
    log error "Empty ${db} field provided"
    return 1
  fi
  if test -z "${index}"; then
    log error "Unsupported ${db} field: '${field}'"
    return 1
  fi
  printf '%s' "$((index-1))"
}


## Description: Get database entry
## Output: Entry
## Return: getent if database doesn't exist
## Usage: get_entry USER DATABASE FIELD
## Example: get_entry user passwd shell
get_entry(){
  log info "${FUNCNAME[0]} $*"
  has getent || return 1
  local user db field index
  local -a entry
  user="${1:-}"
  db="${2:-}"
  field="${3:-}"
  case "${db}" in
    passwd|shadow)
      is_user "${user}" || return 1
      ;;
    group|gshadow)
      is_group "${user}" || return 1
      ;;
  esac
  index="$(get_field "${db}" "${field}")" || return 1
  if test -z "${index}"; then
    log error "No field index for ${db} field '${field}'"
    return 1
  fi
  ## Avoid failing on last empty field adding a field delimiter at last.
  IFS=":" read -ra entry <<<"$(getent -- "${db}" "${user}"):"
  printf '%s' "${entry[$((index))]}"
}
