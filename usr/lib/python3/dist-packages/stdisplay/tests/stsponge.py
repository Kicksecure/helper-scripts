#!/usr/bin/python3 -su
# pylint: disable=missing-module-docstring disable=duplicate-code

## SPDX-FileCopyrightText: 2025 Benjamin Grande M. S. <ben.grande.b@gmail.com>
## SPDX-FileCopyrightText: 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
##
## SPDX-License-Identifier: AGPL-3.0-or-later

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


if __name__ == "__main__":
    unittest.main()
