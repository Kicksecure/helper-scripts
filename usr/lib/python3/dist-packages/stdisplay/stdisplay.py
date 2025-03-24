#!/usr/bin/env python3

## SPDX-FileCopyrightText: 2025 Benjamin Grande M. S. <ben.grande.b@gmail.com>
## SPDX-FileCopyrightText: 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
##
## SPDX-License-Identifier: AGPL-3.0-or-later

"""
Sanitize text to be safely printed to the terminal.
"""

from curses import setupterm, tigetnum, error as curses_error
from os import environ
from re import compile as re_compile, sub as re_sub
from typing import Optional


def get_sgr_support() -> int:
    """Returns number of supported SGR codes.

    Number of supported colors is limited to a number, there is not definition
    of which SGR queries are supported without trying to parse the terminfo
    database.

    To disable SGR support:

    *   Set a non-empty value to the environment variable NO_COLOR; or
    *   Set the environment variable TERM to a terminal that doesn't support
        SGR, such as 'dumb'.

    Returns
    -------
    int
        Number of supported SGR codes.

    Notes
    -----
    Terminfo database is outdated, it may support 24-bit mode and not advertise
    it. Some terminals can convert higher bit modes to lower ones, but there is
    no easy way to know if it is supported or not.
    https://github.com/termstandard/colors?tab=readme-ov-file#querying-the-terminal

    It is possible to query the terminfo database from the shell:

    $ tput -T "$TERM" colors

    $ for term in $(toe -as | awk '{print $2}'); do
        printf '%d %s\n' "$(tput -T "$term" colors || printf '-1')" "$term"
      done | sort -n

    Examples
    --------
    Get SGR code count supported by your terminal:
    >>> get_sgr_support()
    8

    Get SGR code count for any terminal:
    >>> import os
    >>> os.environ["NO_COLOR"] = ""
    >>> os.environ["COLORTERM"] = ""
    >>> os.environ["TERM"] = "xterm-16color"
    >>> get_sgr_support()
    16

    Disable SGR codes:
    >>> import os
    >>> os.environ["NO_COLOR"] = "1"
    >>> get_sgr_support()
    -1
    """
    if environ.get("NO_COLOR"):
        return -1
    if environ.get("COLORTERM") in ("truecolor", "24bit"):
        return 2**24
    try:
        setupterm()
        return tigetnum("colors")
    except curses_error:
        return -2


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
    Patterns for 3-bit and 4-bit SGR is simple:
    >>> exclude_pattern(r"(0*(30|31))", ["0*31"])
    '(?!(?:0*31))(0*(30|31))'

    When excluding 8-bit and 24-bit SGR, a wild matches can be used:
    >>> exclude_pattern(r"(0*38(:|;)0*5(:|;)0*[0-9])", ["0*38;0*5(:|;)[0-9]+"])
    '(?!(?:0*38;0*5(:|;)[0-9]+))(0*38(:|;)0*5(:|;)0*[0-9])'
    """
    exclude_pattern_str = "|".join(negate_pattern)
    exclude_pattern_str = rf"(?!(?:{exclude_pattern_str}))"
    return rf"{exclude_pattern_str}{original_pattern}"


def get_sgr_pattern(
    sgr: Optional[int],
    exclude_sgr: Optional[list[str]],
) -> str:
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
    *   SGR 8-bit and 24-bit can have the separators semicolon ";" or colon ":"
        as long as only one type of separators is used per sequence.

    With the definitions above, we set the following pseudo regex:

    -  3-bit SGR: 0*([3-4][0-7])?m
    -  4-bit SGR: 0*((9|10)[0-7])?m
    -  88 color and 8-bit SGR: <0-107> and 0*[3-4]8(:|;)0*5(:|;)0*<0-255>m
    - 24-bit SGR: 0*[3-4]8(:|;)0*2(:|;)0*<0-255>(:|;)0*<0-255>(:|;)0*<0-255>m

    Where the angle brackets '<>' stands for a pseudo regex range while the
    square brackets '[]' stands for a valid regex range. Remember that any bit
    mode can start, end and be in the middle of a sequence as well as be
    prefixed, separated and terminated by as many semicolons as it wants, while
    separators used in 8-bit and 24-bit SGR have to be consistent. The
    following are examples of valid sequences:

    ESC CSI 38:2:0:0:0:1:38;5;255m
    ESC CSI 38;2;0;0;0;1;38;5;255m
    ESC CSI 038;002;000;000;000;001;038;005;255m
    ESC CSI ;;;;00038;002;00000;00000;000;;;;;001;;;;;;;038;005;0000255;m

    The last sequence is valid but empty parameters ';;' or ';m' resets the
    attributes until that point.

    Parameters
    ----------
    sgr : Optional[int]
        Number of SGR codes the terminal supports.
    exclude_sgr : Optional[list[str]]
        SGR codes to be excluded.

    Returns
    -------
    str
        Compiled regular expression with negative lookahead.

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/ANSI_escape_code
    .. [2] https://invisible-island.net/xterm/ctlseqs/ctlseqs.html
    .. [3] https://man.archlinux.org/man/console_codes.4.en.txt
    .. [4] https://invisible-island.net/ncurses/terminfo.src.html

    Examples
    --------
    Get SGR pattern:
    >>> get_sgr_pattern()

    Get SGR pattern excluding some specific codes:
    >>> exclude_pattern = ["0*30", "0*4[0-7]", "0*38(:|;)0*5(:|;)[0-9]+",
    ...                    "0*38(:|;)0*2(:|;)0*0(:|;)[0-9]+(:|;)0*255"]
    >>> get_sgr_pattern(sgr=2 ** 24, exclude_pattern=exclude_pattern)
    """
    if not sgr or sgr < 8:
        return r"(?!)"

    ## 15: emu
    ## 52: d430*, dg+cc, dgunix+ccc
    ## 64: hpterm-color, wy370*, wyse370
    if sgr >= 2**3:  ## 8 colors
        pal_3bit = r"0*(0|[3-4][0-7])"
        sgr_combo = rf"{pal_3bit}"
    if sgr >= 2**4:  ## 16 colors
        pal_16bit = r"0*(1|9[0-7]|10[0-7])"
        sgr_combo = rf"{sgr_combo}|{pal_16bit}"
    if sgr >= 88:  ## 88 and 256 colors
        ## 88 colors is not well documented but the few terminals that support
        ## it are very common (xterm, rxvt, Eterm). The terminfo library links
        ## the 88 variant to the 256 one with the 'use=' keyword. The "real" 88
        ## color layout is not implemented as the commentator could not
        ## identify it.
        ## https://lists.gnu.org/archive/html/bug-ncurses/2020-03/msg00025.html
        ## TODO: verify which attributes should stay. # pylint: disable=fixme
        pal_88color = r"0*([2-5]|[7-9]|2[1-5]|2[7-9]|39|49)"
        range_8bit = r"0*([0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"
        pal_8bit = rf"0*[3-4]8;0*5;{range_8bit}"
        pal_8bit_std = rf"0*[3-4]8:0*5:{range_8bit}"
        sgr_combo = rf"{sgr_combo}|{pal_88color}|{pal_8bit}|{pal_8bit_std}"
    if sgr >= 2**24:  ## 16777216 colors
        pal_24bit = rf"0*[3-4]8;0*2;{range_8bit};{range_8bit};{range_8bit}"
        pal_24bit_std = rf"0*[3-4]8:0*2:{range_8bit}:{range_8bit}:{range_8bit}"
        sgr_combo = rf"{sgr_combo}|{pal_24bit}|{pal_24bit_std}"

    sgr_combo = rf"({sgr_combo})"
    if exclude_sgr:
        sgr_combo = exclude_pattern(sgr_combo, exclude_sgr)
    sgr_re = rf"(;*({sgr_combo})?(;+{sgr_combo})*)?;*m"
    return str(sgr_re)


def stdisplay(
    untrusted_text: str,
    sgr: Optional[int] = get_sgr_support(),
    exclude_sgr: Optional[list[str]] = None,
) -> str:
    """Sanitize untrusted text to be printed to the terminal.

    Safely print the text passed as argument

    Sanitize input based on an allow list. By default, allows printable ASCII,
    newline (\\n), horizontal tab (\\t) and a subset of SGR (Select Graphic
    Rendition). Illegal characters are replaced with underscores (_).

    Parameters
    ----------
    untrusted_text : str
        The unsafe text to be sanitized.
    sgr : Optional[int] = get_sgr_support()
        Number of SGR codes the terminal supports.
    exclude_sgr : Optional[list[str]] = None
        SGR codes to be excluded.

    Returns
    -------
    str
        Sanitized text.

    Examples
    --------
    Redact unsafe sequences by default:
    >>> stdisplay("\x1b[2Jvulnerable: True\b\b\b\bFalse")
    '_[2Jvulnerable: True____False'

    Redact all SGR codes:
    >>> stdisplay("\x1b[38;5;0m\x1b[31m\x1b[38;2;0;0;0m", sgr=-1)
    '_[38;5;0m_[31m_[38;2;0;0;0m'

    Allow 4-bit SGR but not other bit modes:
    >>> stdisplay("\x1b[38;5;0m\x1b[31m\x1b[38;2;0;0;0m", sgr=2**4)
    '_[38;5;0m\x1b[31m_[38;2;0;0;0m'
    """
    sgr_pattern = get_sgr_pattern(sgr=sgr, exclude_sgr=exclude_sgr)
    sgr_pattern = r"(\x1b(?!\[" + sgr_pattern + r")|[^\x1b\n\t\x20-\x7E])"
    return str(re_sub(re_compile(sgr_pattern), "_", untrusted_text))
