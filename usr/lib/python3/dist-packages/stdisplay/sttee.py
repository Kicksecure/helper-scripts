#!/usr/bin/python3 -su

## Copyright (C) 2025 - 2025 Benjamin Grande M. S. <ben.grande.b@gmail.com>
## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

"""Safely print stdin to stdout and file."""

from contextlib import ExitStack
from sys import argv, stdin, stdout
from typing import TextIO
from stdisplay.stdisplay import stdisplay


def main() -> None:
    """Safely print stdin to stdout and file."""
    stdout.reconfigure(  # type: ignore
        encoding="ascii", errors="replace", newline="\n"
    )
    if stdin is not None:
        stdin.reconfigure(  # type: ignore
            encoding="utf-8", errors="replace", newline="\n"
        )
    with ExitStack() as stack:
        output_files: list[TextIO] = []
        if len(argv) > 1:
            for file_arg in argv[1:]:
                output_files.append(
                    stack.enter_context(
                        open(
                            file_arg,
                            "w",
                            encoding="ascii",
                            errors="replace",
                            newline="\n",
                        )
                    )
                )
        if stdin is not None:
            for untrusted_text in stdin:
                rendered_text: str = stdisplay(untrusted_text)
                stdout.write(rendered_text)
                for output_file in output_files:
                    output_file.write(rendered_text)
        stdout.flush()
