#!/usr/bin/env python3
# pylint: disable=missing-module-docstring

## SPDX-FileCopyrightText: 2025 Benjamin Grande M. S. <ben.grande.b@gmail.com>
## SPDX-FileCopyrightText: 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
##
## SPDX-License-Identifier: AGPL-3.0-or-later

import unittest
import stdisplay.tests


class TestSTTee(stdisplay.tests.TestSTBase):
    """
    Test sttee
    """

    def setUp(self) -> None:
        self.module = "sttee"
        super().setUp()

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
            self._get_file(file=self.tmpfiles["fill"]),
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
            self._get_file(file=self.tmpfiles["fill"]),
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
            self._get_file(file=self.tmpfiles["fill"]),
        )
        self.assertEqual(
            self.text_dirty_sanitized,
            self._get_file(file=self.tmpfiles["fill2"]),
        )


if __name__ == "__main__":
    unittest.main()
