#!/usr/bin/python3 -su

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

# pylint: disable=unknown-option-value

"""
sanitize_string_lib.py: Library for stripping markup and control characters
from a string.
"""

from strip_markup.strip_markup_lib import strip_markup
from stdisplay.stdisplay import stdisplay


def sanitize_string(untrusted_string: str) -> str:
    """
    Sanitizer function.
    """

    ## It isn't necessarily safe to strip ANSI codes first, then markup, since
    ## markup may contain HTML entities that are translated to ESC characters.
    ## CPython's HTML parser is smart enough to discard such entities, but
    ## that could break in the future in theory.
    ##
    ## Similarly, it isn't safe to strip markup first, then ANSI codes, as
    ## there may be a bug (now or in the future) in CPython's HTML parser that
    ## would fail to strip an HTML tag with an embedded ESC character. That
    ## tag could then be activated when the ESCs are translated to underscores
    ## by stdisplay. Thus, we should either strip markup, strip escapes, then
    ## strip markup again, or strip escapes, strip markup, then strip escapes
    ## again.
    ##
    ## In benchmarking, stdisplay is anywhere between three and ten times
    ## faster than strip_markup, thus we use "strip escapes, strip markup,
    ## then strip escapes again."

    step_one_sanitized_string: str = stdisplay(untrusted_string, sgr=-1)
    step_two_sanitized_string: str = strip_markup(step_one_sanitized_string)
    final_sanitized_string: str = stdisplay(step_two_sanitized_string, sgr=-1)
    return final_sanitized_string
