#!/usr/bin/python3 -Bsu

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

# pylint: disable=unknown-option-value

"""
sanitize_string.py: Strips markup and control characters from a string.
"""

import sys
from strip_markup.strip_markup_lib import markup_incomplete
from .sanitize_string_lib import sanitize_string

## Cap on input held back while a markup construct is still open, so an
## unterminated construct cannot buffer without bound. Past it, sanitize what
## has accumulated even though more input could still change its parse.
STDIN_MAX_PENDING_CHARS: int = 65536


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


def write_sanitized(
    untrusted_string: str, remaining: int | None
) -> int | None:
    """
    Sanitize untrusted_string, write it out immediately, and return what is
    left of the output budget.
    """

    sanitized_string: str = sanitize_string(untrusted_string)
    if remaining is not None:
        sanitized_string = sanitized_string[:remaining]
        remaining -= len(sanitized_string)
    sys.stdout.write(sanitized_string)
    ## Not relying on line buffering: sanitizing can consume the newline that
    ## would otherwise have triggered the flush, e.g. one inside a tag.
    sys.stdout.flush()
    return remaining


def sanitize_stdin(max_string_length: int | None) -> int:
    """
    Sanitize standard input as it arrives rather than waiting for end of
    input, so output from a long-running producer appears as it is produced
    instead of arriving in one burst when the producer exits.

    Output is written only where splitting the input cannot change how it is
    sanitized, which keeps this equivalent to sanitizing the whole input at
    once:

    * A line boundary can never fall inside an escape sequence, as no allowed
      sequence can contain a newline -- SGR is composed solely of digits,
      semicolons, colons and the 'm' terminator. This is the same reasoning
      that lets stcat/stcatn/sttee stream; see agents/stdisplay-security.md.
    * Markup can span a line boundary, so lines are held back while a markup
      construct is still open. Otherwise a construct split across lines would
      not be recognised as markup, and content the parser would have consumed
      -- the body of a multi-line comment, say -- would be emitted as text.
    """

    sys.stdin.reconfigure(  # type: ignore
        encoding="utf-8", errors="replace", newline="\n"
    )
    sys.stdout.reconfigure(  # type: ignore
        encoding="ascii", errors="replace", newline="\n"
    )

    remaining: int | None = max_string_length
    if remaining is not None and remaining <= 0:
        return 0

    pending_string: str = ""
    for untrusted_line in sys.stdin:
        pending_string += untrusted_line
        if len(pending_string) < STDIN_MAX_PENDING_CHARS and markup_incomplete(
            pending_string
        ):
            continue
        remaining = write_sanitized(pending_string, remaining)
        pending_string = ""
        ## Stop before reading another line, which would otherwise block on a
        ## producer still running with nothing left for us to emit.
        if remaining is not None and remaining <= 0:
            return 0
    if pending_string:
        write_sanitized(pending_string, remaining)
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
