#!/usr/bin/python3 -su

## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## Authored by Claude (Anthropic).

# pylint: disable=missing-module-docstring

"""
Hypothesis property-based tests for unicode_show.

Properties asserted for ALL inputs:
  - is_suspicious(c) is total (never raises) and returns bool
  - describe_char(c) is total (never raises) and produces a non-empty
    string for every Unicode code point
  - all printable-ASCII codepoints (U+0020..U+007E) except none are
    classified non-suspicious; this is the contract every other
    consumer of unicode_show implicitly relies on
"""

import unittest
from hypothesis import given, strategies as st
from unicode_show.unicode_show import describe_char, is_suspicious


class TestUnicodeShowProperties(unittest.TestCase):
    """Property-based tests for is_suspicious() and describe_char()."""

    @given(st.characters())
    def test_is_suspicious_total_and_bool(self, c: str) -> None:
        """is_suspicious must return bool for any single character."""
        result = is_suspicious(c)
        self.assertIsInstance(result, bool)

    @given(st.characters())
    def test_describe_char_total(self, c: str) -> None:
        """describe_char must return a non-empty str for any character."""
        result = describe_char(c)
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    @given(st.characters(min_codepoint=0x20, max_codepoint=0x7E))
    def test_printable_ascii_not_suspicious(self, c: str) -> None:
        """
        Printable ASCII (U+0020..U+007E) must always be classified
        non-suspicious. If this regresses, the entire 'flag the unusual
        character' contract breaks for the most common input.
        """
        self.assertFalse(
            is_suspicious(c),
            f"printable ASCII {c!r} (U+{ord(c):04X}) flagged as suspicious",
        )


if __name__ == "__main__":
    unittest.main()
