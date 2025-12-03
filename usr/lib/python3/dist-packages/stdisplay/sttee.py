#!/usr/bin/python3 -su

## SPDX-FileCopyrightText: 2025 Benjamin Grande M. S. <ben.grande.b@gmail.com>
## SPDX-FileCopyrightText: 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
##
## SPDX-License-Identifier: AGPL-3.0-or-later

"""Safely print stdin to stdout and file."""
from sys import argv, stdin, stdout, modules
from typing import TextIO
from stdisplay.stdisplay import stdisplay


def main() -> None:
    """Safely print stdin to stdout and file."""
    # https://github.com/pytest-dev/pytest/issues/4843
    if "pytest" not in modules and stdin is not None:
        stdin.reconfigure(errors="replace")  # type: ignore
    output_files: list[TextIO] = []
    try:
        if len(argv) > 1:
            for file_arg in argv[1:]:
                # pylint: disable=consider-using-with
                output_files.append(open(file_arg, "w", encoding="utf-8"))
        if stdin is not None:
            for untrusted_text in stdin:
                rendered_text: str = stdisplay(untrusted_text)
                stdout.write(rendered_text)
                for output_file in output_files:
                    output_file.write(rendered_text)
        stdout.flush()
    finally:
        for output_file in output_files:
            output_file.close()


if __name__ == "__main__":
    main()
