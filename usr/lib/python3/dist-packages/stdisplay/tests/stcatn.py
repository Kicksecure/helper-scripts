#!/usr/bin/env python3

import unittest
import sys
from unittest.mock import patch
from test.support import captured_stdout

# TODO: rewrite
class TestSTCatn(unittest.TestCase):
    """
    Test stcatn.
    """

    def tearDown(self):
        del sys.modules["stdisplay.stcatn"]

    def test_stcatn_no_arg(self):
        """
        Test stcatn without argument.
        """
        argv = ["stcatn.py"]
        with patch.object(sys, "argv", argv), captured_stdout() as stdout:
            import stdisplay.stcatn  # pylint: disable=import-outside-toplevel
            stdisplay.stcatn.main()
        result = stdout.getvalue()
        self.assertEqual("\n", result)

    def test_stcatn_word_split(self):
        """
        Test stcatn word splitting behavior.
        """
        argv = ["stcatn.py", "Hello", "world"]
        with patch.object(sys, "argv", argv), captured_stdout() as stdout:
            import stdisplay.stcatn  # pylint: disable=import-outside-toplevel
            stdisplay.stcatn.main()
        result = stdout.getvalue()
        self.assertEqual("Hello world\n", result)

    def test_stcatn_sanitize(self):
        """
        Test stcatn sanitization.
        """
        argv = ["stcatn.py", "\x1b[0mHello world\x1b[2K"]
        with patch.object(sys, "argv", argv), captured_stdout() as stdout:
            import stdisplay.stcatn  # pylint: disable=import-outside-toplevel
            stdisplay.stcatn.main()
        result = stdout.getvalue()
        self.assertEqual("\x1b[0mHello world_[2K\n", result)


if __name__ == "__main__":
    unittest.main()
