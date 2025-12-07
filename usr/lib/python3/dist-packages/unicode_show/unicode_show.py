#!/usr/bin/python3 -su

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

# pylint: disable=broad-exception-caught

"""
This script scans input text or files for non-ASCII and suspicious Unicode
characters. It prints lines with suspicious characters annotated inline (e.g.,
[U+XXXX]). For each such character, it prints the Unicode codepoint, name, and
category.

Exit codes:
  0 - No suspicious Unicode found
  1 - Suspicious Unicode found
  2 - Error (e.g., file I/O or decoding error)
"""

import sys
import unicodedata
import string
import os
from typing import TextIO

USE_COLOR: bool = False

RED: str = "\033[91m"
CYAN: str = "\033[96m"
RESET: str = "\033[0m"

VISIBLE_ASCII_RANGE: range = range(0x20, 0x7F)
ALLOWED_WHITESPACE: set[str] = {"\n", "\t"}
SAFE_ASCII_SEMANTIC: set[str] = set(
    string.ascii_letters + string.digits + string.punctuation + " \n\t"
)


def colorize(text: str, color: str) -> str:
    """
    Return a string with ANSI color codes applied, if the terminal supports
    color output.
    """

    return f"{color}{text}{RESET}" if USE_COLOR else text


def is_suspicious(c: str) -> bool:
    """
    Check if a character is suspicious or not.
    """

    codepoint_allowed: bool = (
        ord(c) in VISIBLE_ASCII_RANGE or c in ALLOWED_WHITESPACE
    )
    semantically_allowed: bool = c in SAFE_ASCII_SEMANTIC
    ## Purposeful redundancy for extra safety.
    return not (codepoint_allowed and semantically_allowed)


def describe_char(c: str) -> str:
    """
    Return a description of a Unicode character including codepoint, name,
    and category.
    """

    code: int = ord(c)
    name: str = unicodedata.name(c, "<unnamed>")
    cat: str = unicodedata.category(c)

    codepoint_allowed: bool = (
        code in VISIBLE_ASCII_RANGE or c in ALLOWED_WHITESPACE
    )
    semantically_allowed: bool = c in SAFE_ASCII_SEMANTIC

    ## Purposeful redundancy for extra safety in character display.
    display: str
    if codepoint_allowed and semantically_allowed and not c.isspace():
        display = c
    else:
        display = repr(c)

    desc: str = f"{display} (U+{code:04X}, {name}, {cat})"
    return colorize(desc, CYAN)


def scan_line(
    line: str, lineno: int | None = None, filename: str | None = None
) -> bool:
    """
    Scan a single line for suspicious characters, print annotated line and
    character info.
    """

    annotated: str = ""
    has_suspicious: bool = False
    prefix: str = f"{filename or "<stdin>"}:{lineno}: "
    suspicious_descrs: list[str] = []

    for c in line:
        if is_suspicious(c):
            has_suspicious = True
            code: str = f"[U+{ord(c):04X}]"
            annotated += colorize(code, RED)
            suspicious_descrs.append(f"   -> {describe_char(c)}")
        else:
            annotated += c

    if annotated and annotated[-1] == "\n":
        annotated = annotated[:-1]

    annotated_stripped: str = annotated.rstrip()
    ## Trailing whitespaces are suspicious.
    # pylint: disable=line-too-long
    ## https://forums.whonix.org/t/detecting-malicious-unicode-in-source-code-and-pull-requests/13754/28
    if len(annotated) != len(annotated_stripped):
        annotated_new: str = annotated_stripped
        has_suspicious = True
        for c in annotated[len(annotated_stripped) :]:
            code = f"[U+{ord(c):04X}]"
            annotated_new += colorize(code, RED)
            suspicious_descrs.append(f"   -> {describe_char(c)}")
        annotated = annotated_new

    if not has_suspicious:
        return False

    print(prefix + annotated)
    for suspicious_descr in suspicious_descrs:
        print(suspicious_descr)

    return True


def scan_file(f: TextIO, filename: str | None = None) -> bool:
    """
    Scan an entire file-like object for suspicious characters.
    """

    found: bool = False
    last_lineno: int = 0
    ## Empty files should not report "missing newline at end".
    # last_line = ""
    last_line: str | None = None

    for lineno, line in enumerate(f, 1):
        last_lineno = lineno
        last_line = line
        if scan_line(line, lineno=lineno, filename=filename):
            found = True

    if last_line is not None and not last_line.endswith("\n"):
        found = True
        ## Missing newline at the end is suspicious.
        msg: str = f"{filename or "<stdin>"}:{last_lineno}: " + colorize(
            "[missing newline at end]", RED
        )
        print(msg)

    return found


def main() -> int:
    """
    Main function.
    """

    # pylint: disable=global-statement
    global USE_COLOR
    USE_COLOR = (
        not os.getenv("NOCOLOR")
        and os.getenv("NO_COLOR") != "1"
        and os.getenv("TERM") != "dumb"
        and sys.stdout.isatty()
    )

    clean: bool = True
    try:
        if len(sys.argv) > 1:
            for fname in sys.argv[1:]:
                try:
                    ## Must not use errors='replace' because otherwise
                    ## suspicious unicode might slip.
                    ## Fail closed for non-UTF-8.
                    with open(
                        fname,
                        "r",
                        encoding="utf-8",
                        errors="strict",
                        newline="\n",
                    ) as f:
                        if scan_file(f, filename=fname):
                            clean = False
                except UnicodeDecodeError as e:
                    print(
                        f"[ERROR] Unicode decode error [{fname}]: {e}",
                        file=sys.stderr,
                    )
                    clean = False
                except Exception as e:
                    print(
                        f"[ERROR] File read error [{fname}]: {e}",
                        file=sys.stderr,
                    )
                    return 2
        elif sys.stdin is not None:
            try:
                sys.stdin.reconfigure(  # type: ignore
                    encoding="utf-8", errors="strict", newline="\n"
                )
                if scan_file(sys.stdin):
                    clean = False
            except UnicodeDecodeError as e:
                print(
                    f"[ERROR] Unicode decode error [stdin]: {e}",
                    file=sys.stderr,
                )
                clean = False
    except Exception as e:
        print(f"[ERROR] Unexpected error [main]: {e}", file=sys.stderr)
        return 2

    if not clean:
        return 1

    return 0


if __name__ == "__main__":
    main()
