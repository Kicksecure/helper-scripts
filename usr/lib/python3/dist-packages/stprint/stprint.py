#!/usr/bin/env python3

## SPDX-FileCopyrightText: 2025 Benjamin Grande M. S. <ben.grande.b@gmail.com>
## SPDX-FileCopyrightText: 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
##
## SPDX-License-Identifier: AGPL-3.0-or-later

"""
Sanitize text to be safely printed to the terminal.
"""

import re
import sys
from typing import (
    Generator,
    Optional,
    Pattern,
    Union,
)


def exclude_pattern(original_pattern: str, negate_pattern: list[str]) -> str:
    """Exclude matching next expression if provided expression matches.

    Parameters
    ----------
    original_pattern : str
        Pattern which contains unwanted matches.
    negate_pattern : list[str]
        Pattern to exclude from the next match.

    Returns
    -------
    str
        Regular expression with negative lookahead.

    Examples
    --------
    Redact unsafe sequences by default:
    >>> exclude_pattern(r"(0*(30|31))", ["0*31"])
    '(?!(?:0*31))(0*(30|31))'

    Regex in the negating pattern:
    >>> exclude_pattern(r"(0*38;0*5;0*[0-9])", ["0*38;0*5;[0-9]+"])
    '(?!(?:0*38;0*5;[0-9]+))(0*38;0*5;0*[0-9])'
    """
    exclude_pattern_str = "|".join(negate_pattern)
    exclude_pattern_str = rf"(?!(?:{exclude_pattern_str}))"
    return rf"{exclude_pattern_str}{original_pattern}"


def get_color_pattern(
    colors: Optional[bool],
    extra_colors: Optional[bool],
    exclude_colors: Optional[list[str]],
) -> Pattern[str]:
    """Print compiled RegEx for SGR sequences

    The SGR implementation is well documented[1][2][3], here is an extract from
    the Linux manual console_codes(4):

    > The ECMA-48 SGR sequence ESC [ parameters m sets display attributes.
    > Several attributes can be set in the same sequence, separated by
    > semicolons. An empty parameter (between semicolons or string initiator or
    > terminator) is interpreted as a zero.

    But the above is vague, the syntax validation is not strict and assumptions
    were made based on tests using XTerm on Linux, complementing the
    definition:

    *   An empty parameter in the middle of extended SGR 8-bit and higher
        invalidates the sequence.
    *   Can have any semicolons any position (beginning, end and middle),
        except extended SGR 8-bit and higher, as they require to have a single
        semicolon in the middle of the sequence.
    *   Can have 0 prefixing any field of any bit mode. Example normalizing 3
        characters per field (e.g.: ESC CSI 038;002;000;000;150m).
    *   Can have any SGR bit mode in any position (beginning, end, middle).
    *   Specifying a color multiple times will print only the last color
        definition of foreground and background.
    *   Specifying an attribute multiple times will combine them unless they
        revert each other.
    *   Invalid SGR will lead to one of the following behaviors:
        *   Invalidate the whole sequence skipping all SGR.
        *   Invalidate only itself, skipping evaluation of that specific SGR.

    With the definitions above, we set the following pseudo regex:

    -  4-bit SGR: 0*(<0-107>)?m
    -  8-bit SGR: 0*[3-4]8;0*5;0*<0-255>m
    - 24-bit SGR: 0*[3-4]8;0*2;0*<0-255>;0*<0-255>;0*<0-255>m

    Where the angle brackets '<>' stands for a pseudo regex range while the
    square brackets '[]' stands for a valid regex range. Remember that any bit
    mode can start, end and be in the middle of a sequence and be prefixed,
    separated and terminated by as many semicolons as it wants. The following
    are examples of valid sequences:

    ESC CSI 38;2;0;0;0;1;38;5;255m
    ESC CSI 038;002;000;000;000;001;038;005;255m
    ESC CSI ;;;;00038;002;00000;00000;000;;;;;001;;;;;;;038;005;0000255;m

    The last sequence is valid but empty parameters ';;' or ';m' resets the
    attributes until that point.

    Parameters
    ----------
    colors : Optional[bool]
        Whether to allow colors or not.
    extra_colors : Optional[bool]
        Whether to allow extra colors or not.
    exclude_colors : Optional[list[str]]
        Color codes to be excluded.

    Returns
    -------
    str
        Compiled regular expression with negative lookahead.

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/ANSI_escape_code
    .. [2] https://invisible-island.net/xterm/ctlseqs/ctlseqs.html
    .. [3] https://man.archlinux.org/man/console_codes.4.en.txt

    Examples
    --------
    Get pattern for 4-bit colors:
    >>> get_color_pattern(colors=True, extra_colors=False, exclude_pattern="")

    Get pattern for all colors:
    >>> get_color_pattern(colors=True, extra_colors=True, exclude_pattern="")

    Get pattern for all colors excluding some specific colors:
    >>> exclude_pattern = ["0*30", "0*4[0-7]", "0*38;0*5;[0-9]+",
    ...                    "0*38;0*2;0*0;[0-9]+;0*255"]
    >>> get_color_pattern(colors=True, extra_colors=True,
    ...                   exclude_pattern=exclude_pattern)
    """
    if not colors:
        return re.compile(r"(?!)")

    ## TODO: verify which attributes should stay. # pylint: disable=fixme
    sgr_4bit = r"[0-5]|[7-9]|2[1-5]|2[7-9]|3[0-7]|39|4[0-7]|49|9[0-7]|10[0-7]"
    sgr_4bit = rf"0*({sgr_4bit})"
    if exclude_colors:
        sgr_4bit = exclude_pattern(sgr_4bit, exclude_colors)
    sgr_re = rf"(;*({sgr_4bit})?(;+{sgr_4bit})*)?;*m"
    if extra_colors:
        eight_bit = r"0*([0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"
        sgr_8bit = rf"0*[3-4]8;0*5;{eight_bit}"
        sgr_24bit = rf"0*[3-4]8;0*2;{eight_bit};{eight_bit};{eight_bit}"
        sgr_extra = rf"({sgr_4bit}|{sgr_8bit}|{sgr_24bit})"
        if exclude_colors:
            sgr_extra = exclude_pattern(sgr_extra, exclude_colors)
        sgr_re = rf"(;*({sgr_extra})?(;+{sgr_extra})*)?;*m"
    return re.compile(sgr_re)


def gen_output(
    untrusted_text: str,
    sgr_pattern: Optional[Union[str, Pattern[str]]] = None,
) -> Generator[str, str, None]:
    """Create output with a generator.

    Memory efficient method to sanitize the output.

    Parameters
    ----------
    untrusted_text : str
        The unsafe text to be sanitized.
    sgr_pattern : Union[str, Pattern[str]] = re.compile("(?!)")
        Regular expression to match colors.

    Yields
    -------
    str
        Sanitized text.

    Examples
    --------
    Redact every ANSI escape by default:
    >>> list(gen_output("\b\x1b[31m\x1b[m\x1b[2K"))
    ['_', '_', '[', '3', '1', 'm', '_', '[', 'm', '_', '[', '2', 'K']

    Allow just a subset of SGR:
    >>> list(gen_output("\b\x1b[31m\x1b[m\x1b[2K", sgr_pattern="(0|3[0-7])?m"))
    ['_', '\x1b[31m', '\x1b[m', '_', '[', '2', 'K']

    Allow every SGR permissively:
    >>> list(gen_output("\b\x1b[31m\x1b[m\x1b[2K", sgr_pattern="[0-9;]*m"))
    ['_', '\x1b[31m', '\x1b[m', '_', '[', '2', 'K']

    Compile the regex when the pattern is large:
    >>> import re
    >>> regex = r"a very big and distinct regex"
    >>> sgr_pattern = re.compile(regex)
    >>> list(gen_output("\b\x1b[31m\x1b[m\x1b[2K", sgr_pattern=sgr_pattern))
    """
    allowed_space = {ord("\n"), ord("\t")}
    i = 0
    length = len(untrusted_text)
    while i < length:
        char = untrusted_text[i]
        hex_value = ord(char)
        if 0x20 <= hex_value <= 0x7E or hex_value in allowed_space:
            yield char
            i += 1
        elif (
            sgr_pattern
            and hex_value == 0x1B
            and i + 1 < length
            and untrusted_text[i + 1] == "["
            and (sgr_match := re.match(sgr_pattern, untrusted_text[i + 2 :]))
        ):
            ## SGR is only accepted when:
            ## - SGR pattern is not None;
            ## - Character hexadecimal value is ESC (0x1B);
            ## - Character index + 1 is smaller than text length;
            ## - Next character is CSI ([); and
            ## - Regex match starts on the first char after ESC + CSI (i + 2).
            sequence_length = sgr_match.end() + 2
            yield untrusted_text[i : i + sequence_length]
            i += sequence_length
        else:
            yield "_"
            i += 1


def stprint(
    untrusted_text: str,
    colors: Optional[bool] = True,
    extra_colors: Optional[bool] = True,
    exclude_colors: Optional[list[str]] = None,
) -> str:
    """Sanitize untrusted text to be printed to the terminal.

    Safely print the text passed as argument based in an allow list, allowing
    print printable ASCII, newline, tab and a subset of SGR (color and
    formatting codes).

    Parameters
    ----------
    untrusted_text : str
        The unsafe text to be sanitized.
    colors : Optional[bool] = True
        Whether to allow colors or not.
    extra_colors : Optional[bool] = True
        Whether to allow extra colors or not.
    exclude_colors : Optional[list[str]] = None
        Color codes to be excluded.

    Returns
    -------
    str
        Sanitized text.

    Examples
    --------
    Redact unsafe sequences by default:
    >>> stprint("\x1b[2Jvulnerable: True\b\b\b\bFalse")
    '_[2Jvulnerable: True____False'

    Redact all colors:
    >>> stprint("\x1b[38;5;0m\x1b[31m\x1b[38;2;0;0;0m", colors=False)
    '_[38;5;0m_[31m_[38;2;0;0;0m'

    Allow colors but not extra colors bigger than 4bit:
    >>> stprint("\x1b[38;5;0m\x1b[31m\x1b[38;2;0;0;0m", colors=True,
    ...         extra_colors=False)
    '_[38;5;0m\x1b[31m_[38;2;0;0;0m'

    >>> stprint.stprint("\x1b[38;5;0m\x1b[31m\x1b[38;2;0;0;0m",
    ...                 exclude_colors=["0*38;0*(2|5);.*"])
    '_[38;5;0m\x1b[31m_[38;2;0;0;0m'
    """
    sgr_pattern = get_color_pattern(
        colors=colors, extra_colors=extra_colors, exclude_colors=exclude_colors
    )
    return "".join(list(gen_output(untrusted_text, sgr_pattern=sgr_pattern)))


def main() -> None:
    """Sanitize text to be safely printed to the terminal.

    The escapes must be already interpreted for them to be printed as is or
    sanitized.
    """
    untrusted_text = ""
    if len(sys.argv) > 1:
        untrusted_text = "".join(sys.argv[1:])
    else:
        untrusted_text = sys.stdin.buffer.read().decode(
            "ascii", errors="ignore"
        )

    print(stprint(untrusted_text), end="")


if __name__ == "__main__":
    main()
