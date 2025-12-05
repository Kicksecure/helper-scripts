#!/usr/bin/python3 -su

## Copyright (C) 2025 - 2025 Benjamin Grande M. S. <ben.grande.b@gmail.com>
## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

"""Safely print stdin or file to stdout."""

from pathlib import Path
from sys import argv, stdin, stdout, modules
from stdisplay.stdisplay import stdisplay


def main() -> None:
    """Safely print stdin or file to stdout."""
    # https://github.com/pytest-dev/pytest/issues/4843
    if "pytest" not in modules and stdin is not None:
        stdin.reconfigure(errors="replace")  # type: ignore
    if len(argv) == 1:
        if stdin is not None:
            for untrusted_line in stdin:
                stdout.write(stdisplay(untrusted_line))
            stdout.flush()
        return
    for untrusted_arg in argv[1:]:
        if untrusted_arg == "-":
            if stdin is not None:
                for untrusted_line in stdin:
                    stdout.write(stdisplay(untrusted_line))
        else:
            path = Path(untrusted_arg)
            untrusted_text = path.read_text(encoding="utf-8", errors="replace")
            stdout.write(stdisplay(untrusted_text))
    stdout.flush()


if __name__ == "__main__":
    main()
