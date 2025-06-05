#!/usr/bin/env python3

## SPDX-FileCopyrightText: 2025 Benjamin Grande M. S. <ben.grande.b@gmail.com>
## SPDX-FileCopyrightText: 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
##
## SPDX-License-Identifier: AGPL-3.0-or-later

"""
Safely print stdin or file to stdout with tweaks
(trim trailing whitespace, ensure final newline).
"""

from pathlib import Path
from sys import argv, stdin, stdout, modules
from stdisplay.stdisplay import stdisplay


def main() -> None:
    """
    Safely print stdin or file to stdout with tweaks
    (trim trailing whitespace, ensure final newline).
    """
    # https://github.com/pytest-dev/pytest/issues/4843
    if "pytest" not in modules and stdin is not None:
        stdin.reconfigure(errors="ignore")  # type: ignore
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
            path = Path(untrusted_arg)
            untrusted_text = path.read_text(encoding="ascii", errors="replace")
            stdout.write(stdisplay(untrusted_text).rstrip() + "\n")
    stdout.flush()


if __name__ == "__main__":
    main()
