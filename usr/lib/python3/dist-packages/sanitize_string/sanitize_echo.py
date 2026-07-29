#!/usr/bin/python3 -Bsu

## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

# pylint: disable=unknown-option-value

"""
sanitize_echo.py: Print a sanitized string the way echo would.

'stecho' prints with escape sanitization but no length cap. 'sanitize-string'
sanitizes markup as well and caps the length, but writes no trailing newline,
so a caller wanting a diagnostic line had to wrap it in a command substitution
inside another printf. That inline form is the thing this tool exists to
remove: it spawns a subshell per message, and the sanitized value is spliced
back into a format string, which is where a stray '%' or an unquoted expansion
becomes a bug.

This is the union: sanitize-string's sanitizer, echo's shape.
"""

import sys

from .sanitize_string_lib import sanitize_string


def print_usage() -> None:
    """
    Prints usage information.
    """

    print(
        "sanitize-echo: Usage: sanitize-echo [--help] "
        + "[--max-length LENGTH] [--] [string ...]\n"
        + "  Prints the sanitized string(s) followed by a newline.\n"
        + "  Multiple arguments are joined with a single space, as echo "
        + "does.\n"
        + "  If no string is provided, it is read from standard input.\n"
        + "  LENGTH caps the sanitized output; 'nolimit' (the default) "
        + "does not cap it.",
        file=sys.stderr,
    )


def parse_max_length(raw_max_length: str) -> int | None:
    """
    Returns the cap as an int, or None for 'nolimit'. Raises ValueError when
    the value is neither.
    """

    if raw_max_length == "nolimit":
        return None
    max_length: int = int(raw_max_length)
    if max_length < 0:
        raise ValueError("negative length")
    return max_length


def main() -> int:
    """
    Main function.
    """

    max_length: int | None = None
    arg_list: list[str] = sys.argv[1:]

    ## Parse options. Stops at the first non-option so a message that itself
    ## starts with '-' can still be passed after '--'.
    while len(arg_list) > 0:
        arg: str = arg_list[0]
        if arg in ("--help", "-h"):
            print_usage()
            return 0
        if arg == "--":
            arg_list.pop(0)
            break
        if arg == "--max-length":
            if len(arg_list) < 2:
                print_usage()
                return 1
            try:
                max_length = parse_max_length(arg_list[1])
            except ValueError:
                print_usage()
                return 1
            arg_list.pop(0)
            arg_list.pop(0)
            continue
        break

    ## echo semantics: the remaining arguments are the message, joined by a
    ## single space. With none, the message comes from stdin.
    untrusted_string: str
    if len(arg_list) > 0:
        untrusted_string = " ".join(arg_list)
    elif sys.stdin is not None:
        sys.stdin.reconfigure(  # type: ignore
            encoding="utf-8", errors="replace", newline="\n"
        )
        untrusted_string = sys.stdin.read()
    else:
        ## No argument and no stdin: still emit the newline, as echo does.
        untrusted_string = ""

    ## ASCII out, like stecho and sanitize-string: the sanitizer's guarantees
    ## are about the byte stream reaching the terminal, so the encoding must
    ## not reintroduce anything it removed.
    sys.stdout.reconfigure(  # type: ignore
        encoding="ascii", errors="replace", newline="\n"
    )
    sanitized_string: str = sanitize_string(untrusted_string)
    if max_length is not None:
        sanitized_string = sanitized_string[:max_length]
    sys.stdout.write(sanitized_string)
    sys.stdout.write("\n")
    sys.stdout.flush()
    return 0
