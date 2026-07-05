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

    try:
        strip_two_string: str = _strip_once(strip_one_string)
    except Exception:
        return _underscore_sanitize(strip_one_string)

    if strip_one_string != strip_two_string:
        ## The second strip attempt further transformed the text, indicating
        ## an attempt to maliciously circumvent the stripper. Sanitize the
        ## malicious text by underscore-replacing markup metacharacters.
        ##
        ## Note that we sanitize strip_one_string, NOT strip_two_string, so
        ## that the neutered malicious text is displayed to the user. This is
        ## so that the user is alerted to something odd happening.
        return _underscore_sanitize(strip_one_string)

    ## Qt's HTML parser (as used by QTextBrowser) violates the HTML
    ## specification and allows whitespace between the opening `<` character of
    ## a tag and the tag name. Python's parser complies with the spec and does
    ## not consider strings like `< a>` to be tags, thus they are left behind
    ## and Qt will interpret them. We therefore have to remove '<' characters
    ## from the sanitized string even though it no longer contains true HTML at
    ## this point. '>' and '&' alone cannot open a tag, and neutering them
    ## would corrupt legitimate text, so they are left as-is.
    candidate_string: str = strip_one_string.replace("<", "_")

    ## The idempotency check above validated strip_one_string, but the return
    ## value is candidate_string, a DIFFERENT string. Removing a '<' can expose
    ## a character reference that the '<' had shielded from the parser (e.g.
    ## '<...&#66' where the '<' kept the parser out of data mode; once the '<'
    ## becomes '_', a later parse decodes '&#66' to 'B'). candidate_string is
    ## therefore not guaranteed to be a parser fixed point, which would break
    ## the idempotency sanitize_string's double-strip protection relies on. If
    ## re-stripping candidate_string would change it, fall back to full
    ## metacharacter neutering, whose output contains no '<', '>' or '&' and is
    ## thus always a fixed point.
    ##
    ## This is also what makes leaving '&' and '>' in candidate_string safe:
    ## any surviving character reference that decodes to a '<' (e.g. '&lt;',
    ## '&#60;', '&#x3c;') would let a downstream parser revive a tag. Python's
    ## convert_charrefs decodes every such reference, so its presence changes
    ## the re-strip and forces the full-neuter fallback above. The guarantee
    ## therefore holds as long as Python's parser decodes a superset of the
    ## '<'-producing entities any downstream (e.g. Qt) parser would.
    try:
        if _strip_once(candidate_string) == candidate_string:
            return candidate_string
    except Exception:
        ## Re-stripping the candidate raised a parser-internal error, so it
        ## cannot be trusted as a fixed point. Fall through to the
        ## guaranteed-idempotent underscore fallback below.
        pass
    return _underscore_sanitize(strip_one_string)
