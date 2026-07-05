#!/usr/bin/python3 -Bsu

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

# pylint: disable=unknown-option-value,broad-exception-caught

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


def _underscore_sanitize(text: str) -> str:
    """
    Neuter markup metacharacters when the parser path is unsafe.
    See https://stackoverflow.com/a/10371699/19474638
    """

    return "".join("_" if char in ["<", ">", "&"] else char for char in text)


def _strip_once(text: str) -> str:
    """
    Run the markup stripper over text exactly once and return the extracted
    data. Raises on parser-internal failures; callers must fall back to
    _underscore_sanitize so no exception ever reaches the outer caller.
    """

    markup_stripper: StripMarkupEngine = StripMarkupEngine()
    markup_stripper.feed(text)
    markup_stripper.close()
    return markup_stripper.get_data()


def strip_markup(untrusted_string: str) -> str:
    """
    Stripping function.
    """

    try:
        strip_one_string: str = _strip_once(untrusted_string)
    except Exception:
        ## CPython's HTMLParser raises uncaught exceptions on some
        ## malformed inputs (e.g. AssertionError on '<![...' patterns
        ## before gh-77057 landed). Sanitization must never propagate
        ## parser internals to the caller, so fall back to the
        ## underscore strategy on the original input.
        return _underscore_sanitize(untrusted_string)

    ## Previously, we had code here that re-stripped the stripped string,
    ## detected if a second strip changed the string further, and returned a
    ## special "sanitized" version of the single-stripped string if so. This
    ## was intended to allow special characters in strings so long as they did
    ## not form HTML entities or tags. This code has been removed, because:
    ##
    ## * Qt's HTML parser (as used by QTextBrowser) violates the HTML
    ##   specification and allows whitespace between the opening `<` character
    ##   of a tag and the tag name. Python's parser complies with the spec and
    ##   does not consider strings like `< a>` to be tags, thus they are left
    ##   behind and Qt will interpret them.
    ## * When attempting to work around the above issue by only sanitizing out
    ##   '<' characters after a successful strip, we discovered that a
    ##   combination of non-printing characters and '<' characters can
    ##   sometimes fool StripMarkupEngine into not parsing an HTML entity.
    ##   Stripping out just '<' characters but leaving '&' characters in this
    ##   instance would leave entities that downstream consumers may parse.
    ##   This could be worked around by doing a third strip pass, but it's
    ##   unclear what other bugs or strange behaviors we may encounter in the
    ##   future.
    ##
    ## We no longer consider it safe to leave any metacharacters in a string
    ## that is being HTML-stripped. We do a single strip pass, then sanitize
    ## whatever's left unconditionally and return it. This behaves almost the
    ## same as the old code, but '<', '>' and '&' characters are turned into
    ## underscores even if this is not technically necessary to make the
    ## string no longer contain HTML according to the HTML5 specification.

    return _underscore_sanitize(strip_one_string)
