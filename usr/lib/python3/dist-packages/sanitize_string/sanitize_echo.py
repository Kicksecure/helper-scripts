#!/usr/bin/python3 -Bsu

## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

# pylint: disable=unknown-option-value

"""
sanitize_echo.py: Thin wrapper over sanitize-string with different syntax.
"""

import sys

from .sanitize_string import main as sanitize_string_main


def print_usage() -> None:
    """
    Prints usage information.
    """

    print("""\
sanitize-echo: Print a sanitized string.
Usage: sanitize-echo [--help|-h] [--max-length LENGTH] [--] [string...]

Arguments:
  --help|-h     Prints this help message.
  --max-length  Maximum allowable number of output characters, input will be
                truncated past this point. Omit or set to 'nolimit' to allow
                arbitrarily long strings.
  --            End-of-options marker.
  string...     The strings to sanitize. Multiple strings are joined with a
                space. If omitted, the string is read from standard input.""",
        file=sys.stderr,
    )


def main() -> int:
    """
    Main function.
    """

    max_length_str: str | None = None
    arg_list: list[str] = sys.argv[1:]

    ## Process arguments
    while len(arg_list) > 0:
        arg: str = arg_list[0]
        if arg in ("--help", "-h"):
            print_usage()
            return 0
        if arg == "--max-length":
            if len(arg_list) < 2:
                print_usage()
                return 1
            max_length_str = arg_list[1]
            arg_list.pop(0)
            arg_list.pop(0)
            continue
        if arg == "--":
            arg_list.pop(0)
            break
        break

    if max_length_str is None:
        max_length_str = "nolimit"

    untrusted_string: str | None = None
    if len(arg_list) > 0:
        untrusted_string = " ".join(arg_list)

    sys.argv = [
        "sanitize-string", "--no-usage", "--newline", "--", max_length_str
    ]
    if untrusted_string is not None:
        sys.argv.append(untrusted_string)

    return_code: int = sanitize_string_main()
    if return_code == 1:
        print_usage()
    return return_code
