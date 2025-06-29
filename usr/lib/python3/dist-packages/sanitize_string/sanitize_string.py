#!/usr/bin/python3 -su

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

from strip_markup.strip_markup import strip_markup
from stdisplay.stdisplay import stdisplay
from typing import Optional

def sanitize_string(
    untrusted_string: str,
    exclude_sgr: Optional[list[str]] = None
):
    step_one_sanitized_string: str = stdisplay(
        untrusted_string,
        exclude_sgr=exclude_sgr,
    )
    final_sanitized_string: str = strip_markup(step_one_sanitized_string)
    return final_sanitized_string
