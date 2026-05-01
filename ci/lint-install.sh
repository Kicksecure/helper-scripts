#!/bin/bash

## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## AI-Assisted

## Install Debian apt dependencies for the lint workflow
## (.github/workflows/lint.yml).
##
## All linters and build helpers come from the Debian/Ubuntu archive
## (the workflow runs in a debian:* / ubuntu:* matrix container).
##
## 'git config safe.directory' is needed because actions/checkout
## clones with the runner user but the container may treat the
## resulting working tree as a different user; without this, git
## refuses to operate ('detected dubious ownership').

set -o errexit
set -o nounset
set -o pipefail
set -o errtrace

## CI guard. This script runs apt-get install and is intended to run
## inside the lint workflow's container. Refuse to run on a developer
## host unless ALLOW_LOCAL=true is set explicitly.
if [ "${CI:-}" != "true" ] && [ "${ALLOW_LOCAL:-}" != "true" ]; then
  printf '%s\n' "${BASH_SOURCE[0]}: refusing to run outside CI (CI != 'true'). Set ALLOW_LOCAL=true to override." >&2
  exit 1
fi

apt-get update --error-on=any
apt-get dist-upgrade -y
apt-get install -y \
  git python3-pytest pylint mypy black ncurses-term \
  build-essential debhelper dh-python dh-apparmor \
  python3-hypothesis

git config --global --add safe.directory "${GITHUB_WORKSPACE:-$PWD}"
