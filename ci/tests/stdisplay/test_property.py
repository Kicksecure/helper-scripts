#!/usr/bin/python3 -su

## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## AI-Assisted

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
## SGR / OSC / CSI sequences are the SGR-eligible exceptions when sgr support
## is enabled - those are ESC-prefixed sequences that we do sanitize tail
## bytes of, but the leading ESC (U+001B) may survive.
_ALLOWED_CONTROL = {"\n", "\t", "\x1b"}


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
    def test_only_ascii_in_output(self, s: str) -> None:
        """
        Output must be purely 7-bit ASCII, and must not contain control
        characters (U+0000..U+001F or U+007F) other than the documented
        allow-list.
        """
        out = stdisplay(s)
        for ch in out:
            cp = ord(ch)
            if ch in _ALLOWED_CONTROL:
                continue
            if cp < 0x20 or cp > 0x7E:
                self.fail(
                    f"unexpected char U+{cp:04X} in stdisplay output: "
                    f"input={s!r} output={out!r}"
                )


if __name__ == "__main__":
    unittest.main()
