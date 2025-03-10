#!/bin/bash

## Copyright (C) 2025 - 2025 Benjamin Grande M. S. <ben.grande.b@gmail.com>
## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

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

source /usr/libexec/helper-scripts/has.sh
source /usr/libexec/helper-scripts/as_root.sh
source /usr/libexec/helper-scripts/log_run_die.sh


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
  local name
  name="${1:-}"
  ## Syntax based on /etc/adduser.conf NAME_REGEX plus dot and at sign.
  ## This check exists to avoid parsing bugs in other applications on
  ## functions from this script which uses RegEx such as grep.
  if [[ ! ${name} =~ ^[a-z_][-a-z0-9_.@]+\$?$ ]]; then
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
  log info "${FUNCNAME[0]} $*"
  ## Avoid running functions twice.
  if test "${FUNCNAME[1]}" != "get_pass"; then
    as_root
  fi
  local user
  user="${1:-}"
  if test -z "${user}"; then
    log error "No user provided"
    return 1
  fi
  is_name_valid "${user}"
  if has getent; then
    if getent passwd -- "${user}" >/dev/null 2>&1; then
      return 0
    fi
    log error "User does not exist: '${user}'"
    return 1
  fi
  if ! id -- "${user}" >/dev/null 2>&1; then
    log error "User does not exist: '${user}'"
    return 1
  fi
}


## Description: Check if group exists.
## Output: None
## Return: 1 if group does not exist.
## Usage: is_group GROUP
## Example: is_group root
is_group(){
  log info "${FUNCNAME[0]} $*"
  local group group_escaped
  group="${1:-}"
  if test -z "${group}"; then
    log error "No group provided"
    return 1
  fi
  is_name_valid "${group}"
  if has getent; then
    if getent group -- "${group}" >/dev/null 2>&1; then
      return 0
    fi
    log error "Group does not exist: '${group}'"
    return 1
  fi
  group_escaped="$(escape_name "${group}")"
  if ! grep --quiet -- "^${group_escaped}:" /etc/group >/dev/null 2>&1; then
    log error "Group does not exist: '${group}'"
    return 1
  fi
}


## Description: Get user password.
## Output: Password field.
## Usage: get_pass USER
## Example: get_pass user
get_pass(){
  log info "${FUNCNAME[0]} $*"
  as_root
  local user pass user_escaped
  user="${1:-}"
  is_user "${user}"
  if has getent; then
    pass="$(get_entry "${user}" shadow pass)"
  else
    user_escaped="$(escape_name "${user}")"
    pass="$(grep -- "^${user_escaped}:" /etc/shadow)"
    pass="${pass#"${user}:"*}"
    pass="${pass%%":"*}"
  fi
  printf '%s' "${pass}"
}


## Description: Get password without its state.
## Output: Password prefix is trimmed.
## Usage: get_clean_pass USER PREFIX
## Example: get_clean_pass user '!*'
get_clean_pass(){
  log info "${FUNCNAME[0]} $*"
  local user pass symbol
  user="${1:-}"
  is_user "${user}"
  symbol="${2:-"!*"}"
  pass="$(get_pass "${user}")"
  local idx
  for (( idx=0; idx < ${#symbol}; idx++ )); do
    pass="${pass#"${symbol:${idx}:1}"}"
  done
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
  is_user "${user}"
  trim_pass="$(get_clean_pass "${user}" '!*')"
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
  local user
  user="${1:-}"
  is_user "${user}"
  case "$(get_pass "${user}")" in
    "!"*) return 0;;
    *) return 1;;
  esac
}


## Description: Check if password is disabled.
## Output: None
## Return: 0 when disabled, 1 otherwise.
## Usage: is_pass_disabled USER
## Example: is_pass_disabled user
is_pass_disabled(){
  log info "${FUNCNAME[0]} $*"
  local user
  user="${1:-}"
  is_user "${user}"
  case "$(get_pass "${user}")" in
    "*"*|"!*"*) return 0;;
    *) return 1;;
  esac
}


## Description: Lock a password.
## Output: None
## Return: passwd
## Usage: lock_pass USER
## Example: lock_pass user
lock_pass(){
  log info "${FUNCNAME[0]} $*"
  has passwd
  local user
  user="${1:-}"
  is_user "${user}"
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
  has chpasswd
  local user
  user="${1:-}"
  is_user "${user}"
  if ! is_pass_locked "${user}"; then
    return 0
  fi
  ## The tools "passwd" and "usermod" can't unlock when password is empty.
  pass="$(get_clean_pass "${user}" '!')"
  chpasswd --crypt-method NONE <<< "${user}:${pass}"
}


## Description: Disable a password.
## Output: None
## Return: chpasswd
## Usage: disable_pass USER
## Example: disable_pass user
disable_pass(){
  log info "${FUNCNAME[0]} $*"
  has chpasswd
  local user
  user="${1:-}"
  is_user "${user}"
  if is_pass_disabled "${user}"; then
    return 0
  fi
  pass="$(get_clean_pass "${user}")"
  if is_pass_locked "${user}"; then
    chpasswd --crypt-method NONE <<< "${user}:!*${pass}"
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
  has chpasswd
  local user
  user="${1:-}"
  is_user "${user}"
  if ! is_pass_disabled "${user}"; then
    return 0
  fi
  if is_pass_locked "${user}"; then
    pass="$(get_clean_pass "${user}" '!*')"
    chpasswd --crypt-method NONE <<< "${user}:!${pass}"
    return 0
  fi
  pass="$(get_clean_pass "${user}" '*')"
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
        pass) index=2;;
        uid) index=3;;
        gid) index=4;;
        comment) index=5;;
        home) index=6;;
        shell) index=7;;
      esac
      ;;
    shadow)
      case "${field}" in
        pass) index=2;;
        last-pass-change) index=3;;
        min-pass-age) index=4;;
        max-pass-age) index=5;;
        warn-pass-period) index=6;;
        lock-pass-period) index=7;;
        expiration-date) index=8;;
      esac
      ;;
    group)
      case "${field}" in
        pass) index=2;;
        gid) index=3;;
        members) index=4;;
      esac
      ;;
    gshadow)
      case "${field}" in
        pass) index=2;;
        admins) index=3;;
        members) index=4;;
      esac
      ;;
    "") log error "No database provided"; return 1;;
    *) log error "Unsupported database: '${db}'"; return 1;;
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
  has getent
  local user db field index
  local -a entry
  user="${1:-}"
  db="${2:-}"
  field="${3:-}"
  case "${db}" in
    passwd|shadow) is_user "${user}";;
    group|gshadow) is_group "${user}";;
  esac
  index="$(get_field "${db}" "${field}")"
  ## Avoid failing on last empty field adding a field delimiter at last.
  IFS=":" read -ra entry <<<"$(getent -- "${db}" "${user}"):"
  printf '%s' "${entry[$((index))]}"
}
