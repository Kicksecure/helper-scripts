#!/usr/bin/env python3

## SPDX-FileCopyrightText: 2025 Benjamin Grande M. S. <ben.grande.b@gmail.com>
## SPDX-FileCopyrightText: 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
##
## SPDX-License-Identifier: AGPL-3.0-or-later

"""
Safely print stdin or file to stdout with tweaks
(trim trailing whitespace, ensure final newline).
"""

from fileinput import input as file_input
from sys import stdin, stdout, modules
from stdisplay.stdisplay import stdisplay


def main() -> None:
    """
    main
    """
    # https://github.com/pytest-dev/pytest/issues/4843
    if "pytest" not in modules:
        stdin.reconfigure(errors="ignore")  # type: ignore

    for line in file_input(encoding="ascii", errors="replace"):
        stdout.write(stdisplay(line).rstrip() + "\n")

    stdout.flush()


if __name__ == "__main__":
    main()
