#!/usr/bin/env python3

import unittest
import sys
from unittest.mock import patch
from test.support import captured_stdout

class TestSTEcho(unittest.TestCase):
    """
    Test stecho.
    """

    def tearDown(self):
        del sys.modules["stdisplay.stecho"]

    def test_stecho_no_arg(self):
        """
        Test stecho without argument.
        """
        argv = ["stecho.py"]
        with patch.object(sys, "argv", argv), captured_stdout() as stdout:
            import stdisplay.stecho  # pylint: disable=import-outside-toplevel
            stdisplay.stecho.main()
        result = stdout.getvalue()
        self.assertEqual("\n", result)

    def test_stecho_word_split(self):
        """
        Test stecho word splitting behavior.
        """
        argv = ["stecho.py", "Hello", "world"]
        with patch.object(sys, "argv", argv), captured_stdout() as stdout:
            import stdisplay.stecho  # pylint: disable=import-outside-toplevel
            stdisplay.stecho.main()
        result = stdout.getvalue()
        self.assertEqual("Hello world\n", result)

    def test_stecho_sanitize(self):
        """
        Test stecho sanitization.
        """
        argv = ["stecho.py", "\x1b[0mHello world\x1b[2K"]
        with patch.object(sys, "argv", argv), captured_stdout() as stdout:
            import stdisplay.stecho  # pylint: disable=import-outside-toplevel
            stdisplay.stecho.main()
        result = stdout.getvalue()
        self.assertEqual("\x1b[0mHello world_[2K\n", result)


if __name__ == "__main__":
    unittest.main()
