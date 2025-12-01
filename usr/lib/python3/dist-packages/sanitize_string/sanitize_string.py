#!/usr/bin/python3 -su

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

"""
sanitize_string.py: Strips markup and control characters from a string.
"""

import sys
from .sanitize_string_lib import sanitize_string


def print_usage() -> None:
    """
    Prints usage information.
    """

    print(
        "sanitize-string: Usage: sanitize-string [--help] max_length "
        + "[string]\n"
        + "  If no string is provided as an argument, the string is read from "
        + "standard input.\n"
        + "  Set max_length to 'nolimit' to allow arbitrarily long strings.",
        file=sys.stderr,
    )


# pylint: disable=too-many-branches
def main() -> int:
    """
    Main function.
    """

    untrusted_string: str | None = None
    max_string_length: int | None = None

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
        if len(arg_list) > 2 or len(arg_list) < 1:
            print_usage()
            return 1
        if arg_list[0] != "nolimit":
            try:
                max_string_length = int(arg_list[0])
                if max_string_length < 0:
                    print_usage()
                    return 1
            except ValueError:
                print_usage()
                return 1
        if len(arg_list) == 2:
            untrusted_string = arg_list[1]

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
    assert untrusted_string is not None
    sanitized_string: str = sanitize_string(untrusted_string)
    if max_string_length is not None:
        sys.stdout.write(sanitized_string[:max_string_length])
    else:
        sys.stdout.write(sanitized_string)
    return 0


if __name__ == "__main__":
    main()
