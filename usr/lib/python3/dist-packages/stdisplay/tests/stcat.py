#!/usr/bin/env python3

import unittest
import stdisplay.tests

class TestSTCat(stdisplay.tests.TestST):
    """
    Test stcat.
    """

    def setUp(self):
        self.module = "stcat"
        super().setUp()

    def test_stcat_stdin(self):
        """
        Test passing stdin.
        """
        self.assertEqual("", self._test_util())
        self.assertEqual("", self._test_util(incoming=""))
        self.assertEqual("", self._test_util(argv=["-"]))
        self.assertEqual(
            "Hello world", self._test_util(incoming="Hello world")
        )
        self.assertEqual(
            "Hello world",
            self._test_util(argv=["-"], incoming="Hello world"),
        )

    def test_stcat_file(self):
        """
        Test passing files.
        """
        cases = [
            ("", [self.temp_files[0], self.temp_files[0]]),
            ("a b\nc d", [self.temp_files[0], self.temp_files[1]]),
            ("a b\nc d\n", [self.temp_files[0], self.temp_files[2]]),
            ("a b\nc da b\nc d\n", [self.temp_files[1], self.temp_files[2]]),
        ]
        for text, argv in cases:
            with self.subTest(text=text, argv=argv):
                self.assertEqual(text, self._test_util(argv=argv))


if __name__ == "__main__":
    unittest.main()
