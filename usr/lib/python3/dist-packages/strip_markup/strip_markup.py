#!/usr/bin/python3 -su

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

"""
strip_markup.py: Strips HTML-like markup from a string.
"""

import sys
from .strip_markup_lib import strip_markup


def print_usage() -> None:
    """
    Prints usage information.
    """

    print(
        "strip-markup: Usage: strip-markup [--help] [string]\n"
        + "  If no string is provided as an argument, the string is read from "
        + "standard input.",
        file=sys.stderr,
    )


def main() -> int:
    """
    Main function.
    """

    untrusted_string: str | None = None

    ## Process arguments
    if len(sys.argv) > 1:
        ## Parse options
        arg_list: list[str] = sys.argv[1:]
        while len(arg_list) > 0:
            arg = arg_list[0]
            # pylint: disable=no-else-return
            if arg in ("--help", "-h"):
                print_usage()
                return 0
            elif arg == "--":
                arg_list.pop(0)
                break
            else:
                break

        ## Parse positional arguments
        if len(arg_list) > 1:
            print_usage()
            return 1
        untrusted_string = arg_list[0]

    ## Read untrusted_string from stdin if needed
    if untrusted_string is None:
        if sys.stdin is not None:
            if "pytest" not in sys.modules:
                sys.stdin.reconfigure(errors="ignore")  # type: ignore
            untrusted_string = sys.stdin.read()
        else:
            ## No way to get an untrusted string, print nothing and
            ## exit successfully
            return 0

    ## Sanitize and print
    sys.stdout.write(strip_markup(untrusted_string))
    return 0


if __name__ == "__main__":
    main()
