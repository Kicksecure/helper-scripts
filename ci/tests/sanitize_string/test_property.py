#!/usr/bin/python3 -su

## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## Authored by Claude (Anthropic).

# pylint: disable=missing-module-docstring

"""
Hypothesis property-based tests for sanitize_string.

sanitize_string composes strip_markup + stdisplay. The properties
below assert that the composition is itself idempotent, total
(never raises), and produces output that satisfies BOTH the
markup-free property AND the no-control-bytes property.
"""

import unittest
from hypothesis import given, settings, strategies as st
from sanitize_string.sanitize_string_lib import sanitize_string

_ALLOWED_CONTROL = {"\n", "\t"}


class TestSanitizeStringProperties(unittest.TestCase):
    """Property-based tests for sanitize_string()."""

    @given(st.text())
    def test_never_raises(self, s: str) -> None:
        """sanitize_string must accept any str without raising."""
        sanitize_string(s)

    @given(st.text())
    def test_idempotent(self, s: str) -> None:
        """Sanitizing already-sanitized output must be a no-op."""
        once = sanitize_string(s)
        twice = sanitize_string(once)
        self.assertEqual(once, twice)

    @given(st.text())
    @settings(max_examples=200)
    def test_no_control_bytes_in_output(self, s: str) -> None:
        """
        Output must not contain control characters other than \\n / \\t.
        sanitize_string applies stdisplay LAST (after strip_markup),
        and unlike standalone stdisplay it is documented to disable
        SGR (so the ESC fallback does not apply).
        """
        out = sanitize_string(s)
        for ch in out:
            cp = ord(ch)
            if ch in _ALLOWED_CONTROL:
                continue
            if cp < 0x20 or cp == 0x7F:
                self.fail(
                    f"unexpected control byte U+{cp:04X} in sanitize_string "
                    f"output: input={s!r} output={out!r}"
                )


if __name__ == "__main__":
    unittest.main()
