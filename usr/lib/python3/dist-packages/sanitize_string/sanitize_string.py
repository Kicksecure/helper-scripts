#!/usr/bin/python3 -Bsu

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

# pylint: disable=unknown-option-value

"""
sanitize_string.py: Strips markup and control characters from a string.
"""

import os
import sys
from strip_markup.strip_markup_lib import markup_incomplete
from .sanitize_string_lib import sanitize_string

## Cap on how much COMPLETED input is held back while a markup construct is
## still open. Past it, sanitize what has accumulated even though more input
## could still change its parse, which is the one case where sanitizing
## standard input as it arrives differs from sanitizing it all at once.
##
## This bounds the hold-back, not memory in general: a single line is read
## whole, so input containing no newline is still accumulated without limit,
## exactly as reading all of standard input always did.
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


def sanitize_stdin_loop(remaining: int | None) -> int:
    """
    Read standard input and write sanitized output, holding lines back only
    while a markup construct is still open. Factored out of sanitize_stdin so
    the whole loop sits under one BrokenPipeError handler.
    """

    pending_string: str = ""
    for untrusted_line in sys.stdin:
        pending_string += untrusted_line
        ## Only a markup character can leave a construct open, so skip the
        ## parse entirely for input containing none. Without this, re-parsing
        ## the whole pending buffer once per line is quadratic in its length.
        if (
            ("<" in pending_string or "&" in pending_string)
            and len(pending_string) < STDIN_MAX_PENDING_CHARS
            and markup_incomplete(pending_string)
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

    Two cases still differ from sanitizing the whole input at once. Neither can
    emit markup or an escape sequence, since every chunk goes through the full
    sanitizer and strip_markup underscores every surviving '<', '>' and '&':

    * A construct still open at STDIN_MAX_PENDING_CHARS is written anyway, so
      its text is emitted rather than consumed.
    * A construct that makes the parser raise is written too, whereas
      strip_markup would underscore-sanitize the whole input; chunks already
      written cannot be revisited.
    """

    sys.stdin.reconfigure(  # type: ignore
        encoding="utf-8", errors="replace", newline="\n"
    )
    sys.stdout.reconfigure(  # type: ignore
        encoding="ascii", errors="replace", newline="\n"
    )

    if max_string_length is not None and max_string_length <= 0:
        return 0

    try:
        return sanitize_stdin_loop(max_string_length)
    except BrokenPipeError:
        ## Downstream closed early, e.g. piped into head. Exit quietly like any
        ## other filter instead of reporting a traceback, and redirect stdout
        ## to the null device so the interpreter's shutdown flush cannot raise
        ## again.
        try:
            devnull_fd: int = os.open(os.devnull, os.O_WRONLY)
        except OSError:
            ## No null device to redirect onto. Exiting quietly is still the
            ## right outcome; only the shutdown flush is left unguarded.
            return 0
        try:
            os.dup2(devnull_fd, sys.stdout.fileno())
        except (OSError, ValueError):
            ## stdout has no real file descriptor, as when it is a StringIO
            ## under test, so there is nothing to redirect and nothing for the
            ## shutdown flush to fail on either.
            pass
        finally:
            ## dup2 duplicated it onto stdout, so this descriptor is now
            ## redundant either way and would otherwise leak.
            os.close(devnull_fd)
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
