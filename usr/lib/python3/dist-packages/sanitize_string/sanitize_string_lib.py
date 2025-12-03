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

    step_one_sanitized_string: str = stdisplay(untrusted_string, sgr=-1)
    final_sanitized_string: str = strip_markup(step_one_sanitized_string)
    return final_sanitized_string
