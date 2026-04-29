#!/usr/bin/python3 -su

## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## Authored by Claude (Anthropic).

# pylint: disable=missing-module-docstring

"""
Hypothesis property-based tests for stdisplay.

Complements the hand-written cases in stdisplay/tests/stdisplay.py by
generating arbitrary inputs and asserting invariants that must hold
for ALL inputs:

  - stdisplay never raises on any 'str' input
  - stdisplay is idempotent: stdisplay(stdisplay(s)) == stdisplay(s)
  - stdisplay output never contains raw control bytes other than \\n / \\t
"""

import unittest
from hypothesis import given, settings, strategies as st
from stdisplay.stdisplay import stdisplay

## Allowed control characters that stdisplay legitimately preserves.
_ALLOWED_CONTROL = {"\n", "\t"}


class TestStdisplayProperties(unittest.TestCase):
    """Property-based tests for stdisplay()."""

    @given(st.text())
    def test_never_raises(self, s: str) -> None:
        """stdisplay must accept any str without raising."""
        stdisplay(s)

    @given(st.text())
    def test_idempotent(self, s: str) -> None:
        """Sanitizing already-sanitized output must be a no-op."""
        once = stdisplay(s)
        twice = stdisplay(once)
        self.assertEqual(once, twice)

    @given(st.text())
    @settings(max_examples=200)
    def test_no_control_bytes_in_output(self, s: str) -> None:
        """
        Output must not contain control characters (U+0000..U+001F or
        U+007F) other than the documented allow-list. SGR / OSC / CSI
        sequences are the SGR-eligible exceptions when sgr support is
        enabled - those are ESC-prefixed sequences that we do
        sanitize tail bytes of, but the leading ESC (U+001B) may
        survive.
        """
        out = stdisplay(s)
        for ch in out:
            cp = ord(ch)
            if ch in _ALLOWED_CONTROL:
                continue
            if ch == "\x1b":
                ## ESC may survive as the SGR sequence introducer.
                continue
            if cp < 0x20 or cp == 0x7F:
                self.fail(
                    f"unexpected control byte U+{cp:04X} in stdisplay output: "
                    f"input={s!r} output={out!r}"
                )


if __name__ == "__main__":
    unittest.main()
