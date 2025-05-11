#!/usr/bin/env python3
# pylint: disable=missing-module-docstring

## SPDX-FileCopyrightText: 2025 Benjamin Grande M. S. <ben.grande.b@gmail.com>
## SPDX-FileCopyrightText: 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
##
## SPDX-License-Identifier: AGPL-3.0-or-later

import unittest
import stdisplay.tests


class TestSTCatn(stdisplay.tests.TestSTBase):
    """
    Test stcatn.
    """

    def setUp(self) -> None:
        self.module = "stcatn"
        super().setUp()

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
