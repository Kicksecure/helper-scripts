#!/usr/bin/python3 -su

## Copyright (C) 2025 - 2025 Benjamin Grande M. S. <ben.grande.b@gmail.com>
## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

# pylint: disable=missing-module-docstring

import unittest
import stdisplay.tests


class TestSTCatn(stdisplay.tests.TestSTBase):
    """
    Test stcatn.
    """

    def setUp(self) -> None:
        super().setUp()
        self.module = "stcatn"

    def test_stcatn_file(self) -> None:
        """
        Test passing files.
        """
        cases = [
            ("a b\nc d\n", [self.tmpfiles["raw"]]),
            (
                "a b\nc d\na b\nc d\n",
                [self.tmpfiles["raw"], self.tmpfiles["raw"]],
            ),
            (self.text_dirty_sanitized + "\n", [self.tmpfiles["dirty"]]),
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
            "a b\nc d\n",
            self._test_util(stdin="is ignored", argv=[self.tmpfiles["raw"]]),
        )


if __name__ == "__main__":
    unittest.main()
