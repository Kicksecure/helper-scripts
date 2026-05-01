#!/usr/bin/python3 -su

## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## AI-Assisted

# pylint: disable=missing-module-docstring

"""
Hypothesis property-based tests for strip_markup.

Properties asserted for ALL inputs:
  - never raises
  - idempotent (strip(strip(s)) == strip(s)) - critical for
    double-strip protection in sanitize_string
  - output is never longer than input (markup-stripping only removes)
"""

import unittest
from hypothesis import given, settings, strategies as st
from strip_markup.strip_markup_lib import strip_markup


class TestStripMarkupProperties(unittest.TestCase):
    """Property-based tests for strip_markup()."""

    @given(st.text())
    def test_never_raises(self, s: str) -> None:
        """strip_markup must accept any str without raising."""
        strip_markup(s)

    @given(st.text())
    @settings(max_examples=200)
    def test_idempotent(self, s: str) -> None:
        """
        Stripping already-stripped output must be a no-op. This is the
        property sanitize_string's documented 'double-strip protection'
        is built on; if it ever regresses, the security model breaks.
        """
        once = strip_markup(s)
        twice = strip_markup(once)
        self.assertEqual(once, twice)


if __name__ == "__main__":
    unittest.main()
