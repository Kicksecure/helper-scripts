#!/usr/bin/python3 -su

## Copyright (C) 2025 - 2025 Benjamin Grande M. S. <ben.grande.b@gmail.com>
## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

"""Safely print stdin to stdout or file."""

from sys import argv, stdin, stdout, modules
from stdisplay.stdisplay import stdisplay


def main() -> None:
    """Safely print stdin to stdout or file."""
    # https://github.com/pytest-dev/pytest/issues/4843
    if "pytest" not in modules and stdin is not None:
        stdin.reconfigure(errors="replace")  # type: ignore
    untrusted_text_list = []
    if stdin is not None:
        for untrusted_text in stdin:
            untrusted_text_list.append(untrusted_text)
    if len(argv) == 1:
        stdout.write(stdisplay("".join(untrusted_text_list)))
        stdout.flush()
    else:
        for file in argv[1:]:
            with open(
                file, "w", encoding="utf-8", errors="replace"
            ) as out_file:
                out_file.write(stdisplay("".join(untrusted_text_list)))


if __name__ == "__main__":
    main()
