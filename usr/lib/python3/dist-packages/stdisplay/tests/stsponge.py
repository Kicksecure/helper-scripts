#!/usr/bin/python3 -su

## Copyright (C) 2025 - 2025 Benjamin Grande M. S. <ben.grande.b@gmail.com>
## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

# pylint: disable=missing-module-docstring disable=duplicate-code

import unittest
from pathlib import Path
import stdisplay.tests


class TestSTSponge(stdisplay.tests.TestSTBase):
    """
    Test stsponge.
    """

    def setUp(self) -> None:
        self.module = "stsponge"
        super().setUp()

    def test_stsponge(self) -> None:
        """
        Test stsponge.
        """
        self.assertEqual("", self._test_util())
        self.assertEqual("", self._test_util(stdin=""))
        self.assertEqual("stdin", self._test_util(stdin="stdin"))
        # Empty stdin with file argument produces empty stdout and file.
        self.assertEqual("", self._test_util(argv=[self.tmpfiles["fill"]]))
        self.assertEqual(
            "",
            Path(self.tmpfiles["fill"]).read_text(encoding="utf-8"),
        )
        # Empty stdout when writing to file and file sanitization.
        self.assertEqual(
            "",
            self._test_util(
                stdin=self.text_dirty, argv=[self.tmpfiles["fill"]]
            ),
        )
        self.assertEqual(
            self.text_dirty_sanitized,
            Path(self.tmpfiles["fill"]).read_text(encoding="utf-8"),
        )
        # Empty stdout when writing to multiple files and its sanitization.
        self.assertEqual(
            "",
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
            "",
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
            "",
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
