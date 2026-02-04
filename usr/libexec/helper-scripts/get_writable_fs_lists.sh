#!/bin/bash

## Copyright (C) 2012 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

# shellcheck source=./check_runtime.bsh
source /usr/libexec/helper-scripts/check_runtime.bsh

if was_executed "${BASH_SOURCE[0]}"; then
  set -o errexit
  set -o nounset
  set -o errtrace
#  set -o pipefail
fi

safe_writable_fs_list=()
danger_writable_fs_list=()

if [ -z "${proc_mount_contents+x}" ]; then
  proc_mount_contents="$(cat /proc/self/mounts)"
fi

[ -z "${sysfs_prefix+x}" ] && sysfs_prefix=""

while read -r line; do
  IFS=' ' read -r -a line_parts <<< "${line}"
  if [ "${#line_parts[@]}" != '6' ]; then
    continue
  fi
  src_device="${line_parts[0]}"
  mount_point="${line_parts[1]}"
  fs_type="${line_parts[2]}"
  opt_str="${line_parts[3]}"
  is_physical_device='false'
  is_network_drive='false'

  if [[ "${src_device}" =~ ^/dev/ ]]; then
    is_physical_device='true'
    if [ "$(printf '%s' "${src_device}" | sed 's/[^\/]//g' | wc -c)" = 2 ];
      then src_device="${src_device##*/}"
      if [[ "${src_device}" =~ ^(sd|vd|hd|xvd) ]] \
        && [[ "${src_device}" =~ (.*)([0-9]+) ]]; then
        ## cut off any numbers from the end, we don't want them
        src_device="${BASH_REMATCH[1]}"
      elif [[ "${src_device}" =~ (.*[0-9]+)(.+) ]]; then
        ## Assume we're dealing with a device type where the disk ID is like
        ## nbd0 and the partition ID is like nbd0p1 (this is the case for NBD
        ## devices, NVME drives, SD cards, some loop devices, etc.). In this
        ## instance we want to trim off the `p1` part.
        src_device="${BASH_REMATCH[1]}"
      fi
    fi
  elif [[ "${fs_type}" =~ ^(nfs|vboxsf|virtiofs|9pfs) ]]; then
    is_network_drive='true'
  fi

  if [ "${is_physical_device}" = 'true' ] \
    || [ "${is_network_drive}" = 'true' ]; then
    IFS=',' read -r -a opt_parts <<< "${opt_str}"
    rw_found='false'
    for opt_part in "${opt_parts[@]}"; do
      if [ "${opt_part}" = 'rw' ]; then
        rw_found='true'
        break
      fi
    done

    if [ "${rw_found}" = 'true' ]; then
      if ! [[ "${mount_point}" =~ ^/media/ ]] \
        && ! [[ "${mount_point}" =~ ^/mnt/ ]] \
        && ! [ "${mount_point}" = '/media' ] \
        && ! [ "${mount_point}" = '/mnt' ]; then
        danger_writable_fs_list+=( "${mount_point}" )
      elif [ "${is_physical_device}" = 'true' ] \
        && [ -f "${sysfs_prefix}/sys/class/block/${src_device}/removable" ] \
        && [ "$(
          cat "${sysfs_prefix}/sys/class/block/${src_device}/removable"
        )" = '0' ]; then
        danger_writable_fs_list+=( "${mount_point}" )
      else
        safe_writable_fs_list+=( "${mount_point}" )
      fi
    fi
  fi
done <<< "${proc_mount_contents}"

## It's safe to use space here, since the /proc/self/mounts file format uses
## space as a separator and will escape spaces into an octal form `\040`.
printf -v safe_writable_fs_line '%s ' "${safe_writable_fs_list[@]}"
printf '%s\n' "${safe_writable_fs_line% }"
printf -v danger_writable_fs_line '%s ' "${danger_writable_fs_list[@]}"
printf '%s\n' "${danger_writable_fs_line% }"
