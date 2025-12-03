#!/usr/bin/env python3

## SPDX-FileCopyrightText: 2025 Benjamin Grande M. S. <ben.grande.b@gmail.com>
## SPDX-FileCopyrightText: 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
##
## SPDX-License-Identifier: AGPL-3.0-or-later

"""
Safely print stdin or file to stdout with tweaks
(trim trailing whitespace, ensure final newline).
"""

from sys import argv, stdin, stdout, modules
from stdisplay.stdisplay import stdisplay


def main() -> None:
    """
    Safely print stdin or file to stdout with tweaks
    (trim trailing whitespace, ensure final newline).
    """
    # https://github.com/pytest-dev/pytest/issues/4843
    if "pytest" not in modules and stdin is not None:
        stdin.reconfigure(errors="replace")  # type: ignore
    if len(argv) == 1:
        if stdin is not None:
            for untrusted_line in stdin:
                stdout.write(stdisplay(untrusted_line).rstrip() + "\n")
            stdout.flush()
        return
    for untrusted_arg in argv[1:]:
        if untrusted_arg == "-":
            if stdin is not None:
                for untrusted_line in stdin:
                    stdout.write(stdisplay(untrusted_line).rstrip() + "\n")
        else:
            ## We cannot read the entire file in at once like we do with
            ## stcat, since we need to trim trailing whitespace from each
            ## individual line in the file.
            with open(
                untrusted_arg, "r", encoding="utf-8", errors="replace"
            ) as untrusted_file:
                for untrusted_line in untrusted_file:
                    stdout.write(stdisplay(untrusted_line).rstrip() + "\n")
    stdout.flush()


if __name__ == "__main__":
    main()
