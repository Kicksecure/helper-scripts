#!/usr/bin/env python3

import unittest
import sys
from unittest.mock import patch
from test.support import captured_stdout, captured_stdin


class TestSTCat(unittest.TestCase):
    """
    Test stcat.
    """

    def tearDown(self):
        del sys.modules["stdisplay.stcat"]

    # TODO: test reading from file

    def test_stcat_stdin_no_arg(self):
        """
        Test stcat sanitization.
        """
        argv = ["stcat.py"]
        with patch.object(
            sys, "argv", argv
        ), captured_stdout() as stdout, captured_stdin():
            import stdisplay.stcat  # pylint: disable=import-outside-toplevel
            stdisplay.stcat.main()
        result = stdout.getvalue()  # pylint: disable=no-member
        self.assertEqual("", result)

    def test_stcat_stdin_dash_arg(self):
        """
        Test stcat sanitization.
        """
        argv = ["stcat.py", "-"]
        with patch.object(
            sys, "argv", argv
        ), captured_stdout() as stdout, captured_stdin() as stdin:
            import stdisplay.stcat  # pylint: disable=import-outside-toplevel
            stdin.write("Hello world")
            stdin.seek(0)
            stdisplay.stcat.main()
        result = stdout.getvalue()  # pylint: disable=no-member
        self.assertEqual("Hello world", result)


    def test_stcat_stdin(self):
        """
        Test stcat sanitization.
        """
        argv = ["stcat.py"]
        with patch.object(
            sys, "argv", argv
        ), captured_stdout() as stdout, captured_stdin() as stdin:
            import stdisplay.stcat  # pylint: disable=import-outside-toplevel
            stdin.write("Hello world")
            stdin.seek(0)
            stdisplay.stcat.main()
        result = stdout.getvalue()  # pylint: disable=no-member
        self.assertEqual("Hello world", result)


if __name__ == "__main__":
    unittest.main()
