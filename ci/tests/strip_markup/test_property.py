#!/usr/bin/python3 -Bsu

## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## AI-Assisted

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
    def test_output_length(self, s: str) -> None:
        """strip_markup output must never be longer than input"""
        stripped = strip_markup(s)
        self.assertLessEqual(len(stripped), len(s))

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

    def test_idempotent_regression_seeds(self) -> None:
        """
        Deterministic idempotency seeds for inputs found by the Atheris
        harness that the randomized strategies above do not reliably
        rediscover. Each of these once made strip_markup(strip_markup(s))
        != strip_markup(s): the '<' shielded a character reference (e.g.
        '&#7') from the parser, and neutering that '<' to '_' after the
        idempotency check exposed the reference so a later strip decoded
        it. Guard the whole class so a regression fails here, not only in
        the fuzzer.
        """
        ## The original ClusterFuzzLite crash input. Built as its own
        ## explicitly-concatenated literal (not an element in the list below)
        ## so it does not read as a list entry with a forgotten comma.
        crash_input = (
            "\x1a\x00&e\x02[\x7f\x7f\x7f\x7f\x7f7T&&&&#6.&&&#&6&#&\x00\x00"
            "!>\x7f\x7f&7&T&&&&#X6&&#&&e<-\x01&\x006&\x01\x00\x7f&7&T&&&&#X6"
            "&&#&&e<-]\x01&\x006&\x01\x00&\x7f\x7f\x7f\x7f\x7f\x7f\x7f<t\x7f"
            "\x04\x7f7e&T&&&&#66&&&3&66&#&\x00\x00!>\x7f\x7f&7&T&&&&&&e<-\x01"
            "&\x006e!"
        )
        seeds = [
            ## Minimal reduction of the crash above.
            "<T&#7\x00",
            crash_input,
        ]
        for seed in seeds:
            once = strip_markup(seed)
            twice = strip_markup(once)
            self.assertEqual(once, twice, f"not idempotent: {seed!r}")


if __name__ == "__main__":
    unittest.main()
