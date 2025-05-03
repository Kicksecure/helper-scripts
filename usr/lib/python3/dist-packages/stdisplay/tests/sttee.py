#!/usr/bin/env python3

import unittest
import sys
from unittest.mock import patch
from test.support import captured_stdout

# TODO: rewrite
class TestSTTee(unittest.TestCase):
    """
    Test sttee.
    """

    def tearDown(self):
        del sys.modules["stdisplay.sttee"]

    def test_sttee_no_arg(self):
        """
        Test sttee without argument.
        """
        argv = ["sttee.py"]
        with patch.object(sys, "argv", argv), captured_stdout() as stdout:
            import stdisplay.sttee  # pylint: disable=import-outside-toplevel
            stdisplay.sttee.main()
        result = stdout.getvalue()
        self.assertEqual("\n", result)

    def test_sttee_word_split(self):
        """
        Test sttee word splitting behavior.
        """
        argv = ["sttee.py", "Hello", "world"]
        with patch.object(sys, "argv", argv), captured_stdout() as stdout:
            import stdisplay.sttee  # pylint: disable=import-outside-toplevel
            stdisplay.sttee.main()
        result = stdout.getvalue()
        self.assertEqual("Hello world\n", result)

    def test_sttee_sanitize(self):
        """
        Test sttee sanitization.
        """
        argv = ["sttee.py", "\x1b[0mHello world\x1b[2K"]
        with patch.object(sys, "argv", argv), captured_stdout() as stdout:
            import stdisplay.sttee  # pylint: disable=import-outside-toplevel
            stdisplay.sttee.main()
        result = stdout.getvalue()
        self.assertEqual("\x1b[0mHello world_[2K\n", result)


if __name__ == "__main__":
    unittest.main()
