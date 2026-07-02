#!/bin/bash

## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## AI-Assisted

## Install Debian apt dependencies for the lint workflow
## (.github/workflows/lint.yml).
##
## Linters and build helpers come from the Debian/Ubuntu archive (the
## workflow runs in a debian:* / ubuntu:* matrix container), EXCEPT black,
## which is pinned to the trixie (Debian 13 stable) version below.
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
apt-get install -y --no-install-recommends \
  git python3-pytest python3-pip ncurses-term \
  build-essential debhelper dh-python dh-apparmor \
  python3-hypothesis

## Pin the style/type linters (black, pylint, mypy) to the trixie (Debian 13
## stable) versions instead of each container's own archive linters.
## sid/testing/rolling ship NEWER linters that reject code the trixie linters --
## and this repo -- consider clean (newer black reformatted append_shared.py;
## newer pylint flagged its module variable as a mis-named constant), making the
## checks non-reproducible across the matrix. Pin via pip so all four containers
## apply the SAME rules. Not from apt: no single apt suite serves trixie's
## versions to all four containers (sid/testing/ubuntu lack them);
## --break-system-packages is safe in the ephemeral CI container. Keep these in
## sync with Debian stable. (pytest/hypothesis stay from apt -- they gate
## runtime behavior, not version-opinionated style.)
pip install --break-system-packages \
  'black==25.1.0' 'pylint==3.3.4' 'mypy==1.15.0'

git config --global --add safe.directory "${GITHUB_WORKSPACE:-$PWD}"
