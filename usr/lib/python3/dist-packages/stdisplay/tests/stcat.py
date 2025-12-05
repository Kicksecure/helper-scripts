#!/usr/bin/python3 -su

## Copyright (C) 2025 - 2025 Benjamin Grande M. S. <ben.grande.b@gmail.com>
## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

# pylint: disable=missing-module-docstring

import unittest
import stdisplay.tests


class TestSTCat(stdisplay.tests.TestSTBase):
    """
    Test stcat.
    """

    def setUp(self) -> None:
        super().setUp()
        self.module = "stcat"

    def test_stcat_stdin(self) -> None:
        """
        Test passing stdin.
        """
        self.assertEqual("", self._test_util())
        self.assertEqual("", self._test_util(stdin=""))
        self.assertEqual("", self._test_util(argv=["-"]))
        self.assertEqual("a b", self._test_util(stdin="a b"))
        self.assertEqual(
            "a b",
            self._test_util(argv=["-"], stdin="a b"),
        )
        self.assertEqual(
            self.text_dirty_sanitized,
            self._test_util(stdin=self.text_dirty),
        )

    def test_stcat_file(self) -> None:
        """
        Test passing files.
        """
        cases = [
            ("", [self.tmpfiles["empty"], self.tmpfiles["empty"]]),
            ("a b\nc d", [self.tmpfiles["empty"], self.tmpfiles["raw"]]),
            (
                "a b\nc d\n",
                [self.tmpfiles["empty"], self.tmpfiles["newline"]],
            ),
            (
                "a b\nc da b\nc d\n",
                [self.tmpfiles["raw"], self.tmpfiles["newline"]],
            ),
            (self.text_dirty_sanitized, [self.tmpfiles["dirty"]]),
            (
                self.text_malicious_unicode_sanitized,
                [self.tmpfiles["malicious_unicode"]],
            ),
            ("a_b\n", [self.tmpfiles["invalid"]]),
        ]
        for text, argv in cases:
            with self.subTest(text=text, argv=argv):
                self.assertEqual(text, self._test_util(argv=argv))

        self.assertEqual(
            "a b\nc d",
            self._test_util(stdin="is ignored", argv=[self.tmpfiles["raw"]]),
        )


if __name__ == "__main__":
    unittest.main()
