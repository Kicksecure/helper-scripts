#!/usr/bin/env python3

import unittest
import sys
from unittest.mock import patch
from test.support import captured_stdout

# TODO: rewrite
class TestSTSponge(unittest.TestCase):
    """
    Test stsponge.
    """

    def tearDown(self):
        del sys.modules["stdisplay.stsponge"]

    def test_stsponge_no_arg(self):
        """
        Test stsponge without argument.
        """
        argv = ["stsponge.py"]
        with patch.object(sys, "argv", argv), captured_stdout() as stdout:
            import stdisplay.stsponge  # pylint: disable=import-outside-toplevel
            stdisplay.stsponge.main()
        result = stdout.getvalue()
        self.assertEqual("\n", result)

    def test_stsponge_word_split(self):
        """
        Test stsponge word splitting behavior.
        """
        argv = ["stsponge.py", "Hello", "world"]
        with patch.object(sys, "argv", argv), captured_stdout() as stdout:
            import stdisplay.stsponge  # pylint: disable=import-outside-toplevel
            stdisplay.stsponge.main()
        result = stdout.getvalue()
        self.assertEqual("Hello world\n", result)

    def test_stsponge_sanitize(self):
        """
        Test stsponge sanitization.
        """
        argv = ["stsponge.py", "\x1b[0mHello world\x1b[2K"]
        with patch.object(sys, "argv", argv), captured_stdout() as stdout:
            import stdisplay.stsponge  # pylint: disable=import-outside-toplevel
            stdisplay.stsponge.main()
        result = stdout.getvalue()
        self.assertEqual("\x1b[0mHello world_[2K\n", result)


if __name__ == "__main__":
    unittest.main()
