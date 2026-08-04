#!/usr/bin/python3 -Bsu

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

# pylint: disable=unknown-option-value

"""
sanitize_string.py: Strips markup and control characters from a string.
"""

import contextlib
import os
import sys
from .sanitize_string_lib import sanitize_string


suppress_usage_info: bool = False


def _silence_broken_pipe_on_shutdown() -> None:
    """
    Redirect stdout to /dev/null after a BrokenPipeError so the interpreter's
    implicit flush of sys.stdout at shutdown does not re-raise BrokenPipeError
    from the C-level finalizer -- which prints an 'Exception ignored on
    flushing sys.stdout' traceback to stderr. The downstream pipe is already
    gone, so nothing more is written anyway; this keeps the immediate-exit
    behavior while suppressing the shutdown noise.
    """

    ## contextlib.suppress rather than a bare 'except OSError: pass' (an empty
    ## except is a smell); the try/finally closes the fd dup2 duplicated, so it
    ## is not leaked even though the process is about to exit.
    with contextlib.suppress(OSError):
        devnull_fd: int = os.open(os.devnull, os.O_WRONLY)
        try:
            os.dup2(devnull_fd, sys.stdout.fileno())
        finally:
            os.close(devnull_fd)


def print_usage() -> None:
    """
    Prints usage information.
    """

    if suppress_usage_info:
        return
    # pylint: disable=line-too-long
    print(
        """\
sanitize-string: Strip / sanitize dangerous control characters and markup.
Usage: sanitize-string [--help|-h] [--no-block] [--no-usage] [--newline] [--] max_length [string]

Arguments:
  --help|-h   Prints this help message.
  --no-block  When reading from stdin, sanitize line by line rather than
              buffering all input first. The string must not be provided as an
              argument if this option is specified. Note that this option may
              cause neutralized HTML to appear in sanitize-string's output
              that would have been stripped otherwise.
  --no-usage  If an error occurs when parsing arguments, do not print usage
              information.
  --newline   Append a new line to the output.
  --          End-of-options marker.
  max_length  Maximum allowable number of output characters, input will be
              truncated past this point. Set to 'nolimit' to allow arbitrarily
              long strings.
  string      The string to sanitize. If omitted, the string is read from
              standard input.""",
        file=sys.stderr,
    )


def sanitize_stdin_noblock(
    max_string_length: int | None, append_newline: bool
) -> int:
    """
    Sanitize standard input one line at a time.
    """

    try:
        for untrusted_line in sys.stdin:
            sanitized_string: str = sanitize_string(untrusted_line)
            if max_string_length is not None:
                sanitized_string = sanitized_string[:max_string_length]
                max_string_length -= len(sanitized_string)
            sys.stdout.write(sanitized_string)
            sys.stdout.flush()
            if max_string_length is not None and max_string_length <= 0:
                break
        if append_newline:
            sys.stdout.write("\n")
        return 0
    except BrokenPipeError:
        ## Downstream closed early, e.g. piped into head. Exit without an
        ## error. This *will* break the pipe of whatever is sending this
        ## script text to sanitize, mirroring the behavior of coreutils (where
        ## `cat /dev/zero | tee /dev/null | head -c1` exits when `head` exits,
        ## rather than running forever with `cat` feeding into a
        ## "fault-tolerant" `tee`).
        _silence_broken_pipe_on_shutdown()
        return 0


def sanitize_block(
    untrusted_string: str, max_string_length: int | None, append_newline: bool
) -> None:
    """
    Sanitize the entire provided string at once.
    """

    assert untrusted_string is not None
    sanitized_string: str = sanitize_string(untrusted_string)
    try:
        if max_string_length is not None:
            sys.stdout.write(sanitized_string[:max_string_length])
        else:
            sys.stdout.write(sanitized_string)
        if append_newline:
            sys.stdout.write("\n")
    except BrokenPipeError:
        ## Not worth erroring out for.
        _silence_broken_pipe_on_shutdown()


# pylint: disable=too-many-branches,too-many-return-statements
def main() -> int:
    """
    Main function.
    """

    # pylint: disable=global-statement
    global suppress_usage_info

    untrusted_string: str | None = None
    max_string_length: int | None = None
    no_block: bool = False
    append_newline: bool = False
    arg_list: list[str] = sys.argv[1:]

    ## Process arguments
    while len(arg_list) > 0:
        arg: str = arg_list[0]
        if arg in ("--help", "-h"):
            print_usage()
            return 0
        if arg == "--no-block":
            no_block = True
            arg_list.pop(0)
            continue
        if arg == "--no-usage":
            suppress_usage_info = True
            arg_list.pop(0)
            continue
        if arg == "--newline":
            append_newline = True
            arg_list.pop(0)
            continue
        if arg == "--":
            arg_list.pop(0)
            break
        break

    if not 1 <= len(arg_list) <= 2:
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

    if untrusted_string is not None and no_block:
        print_usage()
        return 1

    ## Prepare to print output
    sys.stdout.reconfigure(  # type: ignore
        encoding="ascii", errors="replace", newline="\n"
    )

    ## A zero limit emits no sanitized content and must return without reading
    ## stdin, but '--newline' still has to append its newline (as it does for
    ## every other limit), so emit just that and stop.
    if max_string_length == 0:
        if append_newline:
            sanitize_block("", max_string_length, append_newline)
        return 0

    ## Sanitize standard input if no string was given as an argument
    if untrusted_string is None:
        if sys.stdin is None:
            ## No way to get an untrusted string, print nothing and
            ## exit successfully
            return 0
        sys.stdin.reconfigure(  # type: ignore
            encoding="utf-8", errors="replace", newline="\n"
        )

        if no_block:
            ## Dispatch to line-by-line sanitizer, do not run the rest of this
            ## function
            return sanitize_stdin_noblock(max_string_length, append_newline)

        untrusted_string = sys.stdin.read()

    sanitize_block(untrusted_string, max_string_length, append_newline)
    return 0
