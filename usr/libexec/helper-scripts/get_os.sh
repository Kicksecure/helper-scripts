#!/bin/bash

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## TODO: how to handle installer specific code?

source /usr/libexec/helper-scripts/log_run_die.sh
source /usr/libexec/helper-scripts/ip_syntax.sh

## Get host os and other necessary information.
get_os(){
  ## Source: pfetch: https://github.com/dylanaraps/pfetch/blob/master/pfetch
  os="$(uname -s)"
  kernel="$(uname -r)"
  arch="$(uname -m)"

  distro=""
  distro_version=""
  debian_testing_or_unstable_detected=""
  distro_codename=""
  case "${os}" in
    Linux*)
      if has lsb_release; then
        distro="$(lsb_release --short --description || lsb_release -sd)"
        distro_version="$(lsb_release --short --release || lsb_release -sr)"
        distro_codename="$(lsb_release --short --codename || lsb_release -sc)"
      elif test -f /etc/os-release; then
        while IFS='=' read -r key val; do
          case "${key}" in
            (PRETTY_NAME) distro="${val}"
              ;;
            (VERSION_ID) distro_version="${val}"
              ;;
            (VERSION_CODENAME) distro_codename="${val}"
              ;;
          esac
        done < /etc/os-release
      else
        has crux && distro="$(crux)"
        has guix && distro='Guix System'
      fi
      distro="${distro##[\"\']}"
      distro="${distro%%[\"\']}"
      case "${PATH}" in (*/bedrock/cross/*) distro='Bedrock Linux' ;; esac
      if [ "${WSLENV:-}" ]; then
        distro="${distro}${WSLENV+ on Windows 10 [WSL2]}"
      elif [ -z "${kernel%%*-Microsoft}" ]; then
        distro="${distro} on Windows 10 [WSL1]"
      fi
    ;;
    Haiku) distro=$(uname -sv);;
    Minix|DragonFly) distro="${os} ${kernel}";;
    SunOS) IFS='(' read -r distro _ < /etc/release;;
    OpenBSD*) distro="$(uname -sr)";;
    FreeBSD) distro="${os} $(freebsd-version)";;
    *) distro="${os} ${kernel}";;
  esac

  ## Debian 'testing' /etc/os-release does not contain VERSION_ID.
  if printf '%s' "${distro}" | grep "/sid" &>/dev/null ; then
    log info "Debian 'testing' or 'unstable' detection: '/sid' matched"
    debian_testing_or_unstable_detected=1
  fi

  if [ "$distro_codename" = "trixie" ]; then
    log info "Debian 'testing' or 'unstable' detection: 'trixie' still considered 'testing' (hardcoded in this program)"
    debian_testing_or_unstable_detected=1
  fi

  distro_derivative_name_pretty="(No derivative detected.)"
  distro_derivative_version="(No derivative detected.)"
  if test -f /usr/share/kicksecure/marker; then
    distro_derivative_name_pretty="Kicksecure"
    distro_derivative_version="$(cat -- /etc/kicksecure_version)"
  elif test -f /usr/share/whonix/marker; then
    distro_derivative_name_pretty="Whonix"
    distro_derivative_version="$(cat -- /etc/whonix_version)"
  fi

  log notice "Architecture detected: '${arch}'"
  log notice "System detected: '${os}'"
  log notice "Distribution/Derivative name detected: '${distro}' / '${distro_derivative_name_pretty}'"
  log notice "Distribution/Derivative version detected: '${distro_version}' / '${distro_derivative_version}'"

  if [ "$debian_testing_or_unstable_detected" = "1" ]; then
    log notice "Debian 'testing' or 'unstable' detection: 'yes', detected"
    if test "${oracle_repo}" = "1"; then
      log error "You are attempting to use '--oracle-repo' on Debian 'testing' or 'unstable'. This is impossible."
      if test "${ci}" = "1"; then
        die 0 "${underline}Distribution Test Result:${nounderline} Oracle doesn't provide a Debian 'testing' or 'unstable' repository. Skipped on CI to avoid breaking the CI 'testing' or 'unstable'."
      else
        die 101 "${underline}Distribution Test Result:${nounderline} Oracle doesn't provide a Debian 'testing' or 'unstable' repository."
      fi
    fi
    log info "Not attempting to use '--oracle-repo' on Debian 'testing' or 'unstable', good."
    ## In Debian 'testing' distro_version was previously observed as 'n/a' or empty, because
    ## Debian 'testing' '/etc/os-release' does not contain VERSION_ID.
    return 0
  fi
  log info "Debian 'testing' or 'unstable' detection: 'no', not detected"

  ## This at last so the user can hopefully post his system info from the
  ## logs before the error below.
  if [ -z "${distro_version}" ]; then
    if test -f /etc/os-release; then
      log notice "Contents of '/etc/os-release' file:"
      cat -- /etc/os-release || true
    else
      log notice "'/etc/os-release' file not found."
    fi
    die 101 "${underline}Distribution Check:${nounderline} Failed to find distribution version."
    ## it will fail later on get_host_pkgs if the system is not supported.
    ## but distro version needs to be checked here because it can occur
    ## frequently when the release of the distribution is still unstable.
    ## Also because we check for distribution version to abort if necessary.
  fi

  distro_version_without_dot="$(printf '%s' "${distro_version}" | tr -d ".")"
  is_integer "${distro_version_without_dot}" ||
     die 101 "${underline}Distribution Check:${nounderline} Distribution version without dot is still not a number: '${distro_version_without_dot}'"
}


get_distro() {
  true "distro: ${distro}"
  case "${os}" in
    Linux*)
      case "${distro}" in
        [Dd]"ebian"*|[Tt]"ails"*|[Kk]"icksecure"|[Ww]"honix")
          debian_derivative_detected=1
          ;;
        [Kk]"ali"*)
          debian_derivative_detected=1
          kali_derivative_detected=1
          ;;
        "linux mint"*|"linuxmint"*|"Linux Mint"*|"LinuxMint"*|"mint"*)
          ubuntu_derivative_detected=1
          debian_derivative_detected=1
          ;;
        *"buntu"*)
          ubuntu_derivative_detected=1
          debian_derivative_detected=1
          if [ "${distro_version_without_dot}" -lt 2204 ]; then
            die 101 "${underline}Distribution Check:${nounderline} Minimal '${distro}' required version is '22.04', yours is '${distro_version}'."
          fi
          ;;
        [Ff]"edora"*|"centos"*|"CentOS"*|"rhel"*|"red hat"|"redhat"*|"Redhat"*|"Red hat")
          fedora_derivative_detected=1
          ;;
        [Aa]"rch"*|[Aa]"rtix"*|"arcolinux"*|"ArcoLinux"*)
          claim_unsupported_distro known "${distro}"
          ;;
        *)
          claim_unsupported_distro unknown "${distro}"
          ;;
      esac
    ;;
    "openbsd"*|"OpenBSD"*)
      claim_unsupported_distro known "${distro}"
      ;;
    "netbsd"*|"NetBSD"*)
      claim_unsupported_distro known "${distro}"
      ;;
    "freebsd"*|"hardenedbsd"*|"dragonfly"*|"FreeBSD"*|"HardenedBSD"*|"DragonFly"*)
      claim_unsupported_distro known "${distro}"
      ;;
    *)
      claim_unsupported_distro unknown "${distro}"
      ;;
  esac

  if test "${oracle_repo:-}" = "1" && test "${kali_derivative_detected:-}"; then
    die 1 "Distribution Extended Check: Oracle repository does not work with Kali."
  fi

  if test ! "${fedora_derivative_detected:-}" = "1" ||
    test ! "${ci-}" = "1" ||
    test ! "${onion-}" = "1"
  then
    return 0
  fi

  die 0 "${underline}Distribution Test Result:${nounderline} Fedora on CI does not run the Tor systemd service. Skipped on CI to avoid breaking the CI testing."
}
