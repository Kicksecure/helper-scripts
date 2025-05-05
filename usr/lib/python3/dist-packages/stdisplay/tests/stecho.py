#!/usr/bin/env python3
# pylint: disable=missing-module-docstring

## SPDX-FileCopyrightText: 2025 Benjamin Grande M. S. <ben.grande.b@gmail.com>
## SPDX-FileCopyrightText: 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
##
## SPDX-License-Identifier: AGPL-3.0-or-later

import unittest
import stdisplay.tests


class TestSTEcho(stdisplay.tests.TestSTBase):
    """
    Test stecho.
    """

    def setUp(self) -> None:
        self.module = "stecho"
        super().setUp()

    def test_stecho(self) -> None:
        """
        Test stecho.
        """
        self.assertEqual("\n", self._test_util())
        self.assertEqual("\n", self._test_util(argv=[""]))
        self.assertEqual("\n", self._test_util(stdin="no stdin"))
        self.assertEqual("a b\n", self._test_util(argv=["a b"]))
        self.assertEqual("a b\n", self._test_util(argv=["a", "b"]))
        self.assertEqual(
            self.text_dirty_sanitized + "\n",
            self._test_util(argv=[self.text_dirty]),
        )


if __name__ == "__main__":
    unittest.main()
