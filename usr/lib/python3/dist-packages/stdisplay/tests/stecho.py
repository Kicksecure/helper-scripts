#!/usr/bin/python3 -su
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
        self.assertEqual(
            self.text_malicious_unicode_sanitized + "\n",
            self._test_util(argv=[self.text_malicious_unicode]),
        )
        ## \udcff == surrogate escape for 'ff' byte, this is what the string
        ## in sys.argv would contain if running `stecho $'a\xffb\n'`
        self.assertEqual("a_b\n\n", self._test_util(argv=["a\udcffb\n"]))


if __name__ == "__main__":
    unittest.main()
