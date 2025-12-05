#!/usr/bin/python3 -su

## Copyright (C) 2025 - 2025 Benjamin Grande M. S. <ben.grande.b@gmail.com>
## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

# pylint: disable=missing-module-docstring

import unittest
from pathlib import Path
import stdisplay.tests


class TestSTTee(stdisplay.tests.TestSTBase):
    """
    Test sttee
    """

    def setUp(self) -> None:
        super().setUp()
        self.module = "sttee"

    def test_sttee(self) -> None:
        """
        Test sttee.
        """
        self.assertEqual("", self._test_util())
        self.assertEqual("", self._test_util(stdin=""))
        self.assertEqual("stdin", self._test_util(stdin="stdin"))
        # Empty stdin with file argument.
        self.assertEqual("", self._test_util(argv=[self.tmpfiles["fill"]]))
        self.assertEqual(
            "",
            Path(self.tmpfiles["fill"]).read_text(encoding="utf-8"),
        )
        # Stdin sanitization and writing to file.
        self.assertEqual(
            self.text_dirty_sanitized,
            self._test_util(
                stdin=self.text_dirty, argv=[self.tmpfiles["fill"]]
            ),
        )
        self.assertEqual(
            self.text_dirty_sanitized,
            Path(self.tmpfiles["fill"]).read_text(encoding="utf-8"),
        )
        # Stdin sanitization and writing to multiple files.
        self.assertEqual(
            self.text_dirty_sanitized,
            self._test_util(
                stdin=self.text_dirty,
                argv=[self.tmpfiles["fill"], self.tmpfiles["fill2"]],
            ),
        )
        self.assertEqual(
            self.text_dirty_sanitized,
            Path(self.tmpfiles["fill"]).read_text(encoding="utf-8"),
        )
        self.assertEqual(
            self.text_dirty_sanitized,
            Path(self.tmpfiles["fill2"]).read_text(encoding="utf-8"),
        )
        # Proper handling of invalid bytes, \udcff = surrogate escape for 'ff'
        # byte, which is how Python interprets such bytes into strings
        self.assertEqual("a_b\n", self._test_util(stdin="a\udcffb\n"))
        self.assertEqual(
            "a_b\n",
            self._test_util(stdin="a\udcffb\n", argv=[self.tmpfiles["fill"]]),
        )
        self.assertEqual(
            "a_b\n",
            Path(self.tmpfiles["fill"]).read_text(encoding="utf-8"),
        )
        # Proper handling of malicious Unicode
        self.assertEqual(
            self.text_malicious_unicode_sanitized,
            self._test_util(stdin=self.text_malicious_unicode),
        )
        self.assertEqual(
            self.text_malicious_unicode_sanitized,
            self._test_util(
                stdin=self.text_malicious_unicode,
                argv=[self.tmpfiles["fill"]],
            ),
        )
        self.assertEqual(
            self.text_malicious_unicode_sanitized,
            Path(self.tmpfiles["fill"]).read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
