#!/usr/bin/python3 -su

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

"""
strip_markup_lib.py: Library for stripping markup from a string.
"""

from io import StringIO
from html.parser import HTMLParser


## Inspired by https://stackoverflow.com/a/925630/19474638
class StripMarkupEngine(HTMLParser):
    """
    HTMLParser derivative that strips markup tags from its input.
    """

    def __init__(self) -> None:
        """
        Init function.
        """

        super().__init__()
        self.reset()
        self.convert_charrefs = True
        self.text: StringIO = StringIO()

    def handle_data(self, data: str) -> None:
        """
        Accumulates text extracted from markup.
        """

        self.text.write(data)

    def get_data(self) -> str:
        """
        Returns accumulated text extracted from markup.
        """

        return self.text.getvalue()


def strip_markup(untrusted_string: str) -> str:
    """
    Stripping function.
    """

    markup_stripper: StripMarkupEngine = StripMarkupEngine()
    markup_stripper.feed(untrusted_string)
    strip_one_string: str = markup_stripper.get_data()
    markup_stripper = StripMarkupEngine()
    markup_stripper.feed(strip_one_string)
    strip_two_string: str = markup_stripper.get_data()
    if strip_one_string == strip_two_string:
        return strip_one_string

    ## If we get this far, the second strip attempt further transformed the
    ## text, indicating an attempt to maliciously circumvent the stripper.
    ## Sanitize the malicious text by changing all '<', '>', and '&'
    ## characters to underscores. See
    ## https://stackoverflow.com/a/10371699/19474638
    ##
    ## Note that we sanitize strip_one_string, NOT strip_two_string, so that
    ## the neutered malicious text is displayed to the user. This is so that
    ## the user is alerted to something odd happening.
    sanitized_string: str = "".join(
        "_" if char in ["<", ">", "&"] else char for char in strip_one_string
    )
    return sanitized_string
