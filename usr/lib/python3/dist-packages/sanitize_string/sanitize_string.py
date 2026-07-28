#!/usr/bin/python3 -Bsu

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

# pylint: disable=unknown-option-value

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


def sanitize_stdin(max_string_length: int | None) -> int:
    """
    Sanitize standard input line by line, writing each line as soon as it is
    read rather than waiting for end of input, so output from a long-running
    producer appears as it is produced instead of arriving in one burst when
    the producer exits.

    Sanitizing per line rather than over the whole input is safe:

    * No allowed escape sequence can contain a newline -- SGR is composed
      solely of digits, semicolons, colons and the 'm' terminator -- so a line
      boundary can never fall inside one. This is the same reasoning that lets
      stcat/stcatn/sttee stream; see agents/stdisplay-security.md.
    * Markup may span a line boundary, and a tag split that way is not
      recognised as a tag. That cannot leak markup, because strip_markup()
      unconditionally turns every '<', '>' and '&' surviving the parser into
      an underscore. Such a tag's inert text is retained rather than dropped,
      which is the only observable difference from whole-input sanitizing.
    """

    sys.stdin.reconfigure(  # type: ignore
        encoding="utf-8", errors="replace", newline="\n"
    )
    sys.stdout.reconfigure(  # type: ignore
        encoding="ascii", errors="replace", newline="\n", line_buffering=True
    )

    remaining: int | None = max_string_length
    for untrusted_line in sys.stdin:
        if remaining is not None and remaining <= 0:
            break
        sanitized_line: str = sanitize_string(untrusted_line)
        if remaining is not None:
            sanitized_line = sanitized_line[:remaining]
            remaining -= len(sanitized_line)
        sys.stdout.write(sanitized_line)
    return 0


# pylint: disable=too-many-branches,too-many-return-statements
def main() -> int:
    """
    Main function.
    """

    untrusted_string: str | None = None
    max_string_length: int | None = None

    ## Process arguments
    if len(sys.argv) < 2:
        print_usage()
        return 1
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

    ## Sanitize standard input if no string was given as an argument
    if untrusted_string is None:
        if sys.stdin is None:
            ## No way to get an untrusted string, print nothing and
            ## exit successfully
            return 0
        return sanitize_stdin(max_string_length)

    ## Sanitize and print
    sys.stdout.reconfigure(  # type: ignore
        encoding="ascii", errors="replace", newline="\n"
    )
    sanitized_string: str = sanitize_string(untrusted_string)
    if max_string_length is not None:
        sys.stdout.write(sanitized_string[:max_string_length])
    else:
        sys.stdout.write(sanitized_string)
    return 0
