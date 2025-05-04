#!/usr/bin/env python3

import os
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch
from test.support import captured_stdout, captured_stdin


class TestSTCat(unittest.TestCase):
    """
    Test stcat.
    """

    def setUp(self):
        self.temp_files = []
        contents = ["a b\n", "c d"]
        i = 0
        self.temp_dir = tempfile.mkdtemp(prefix="test_stcat_")
        while i < 3:
            self.temp_files.append(os.path.join(self.temp_dir, str(i)))
            with open(self.temp_files[i], "w", encoding="utf-8") as file:
                if i == 0:
                    file.write("")
                elif i == 1:
                    file.write("".join(contents))
                elif i == 2:
                    file.write("".join(contents) + "\n")
                file.flush()
                file.close()
            i += 1

    def tearDown(self):
        del sys.modules["stdisplay.stcat"]
        shutil.rmtree(self.temp_dir)

    def _del_module(self):
        module_name = "stdisplay.stcat"
        if module_name in sys.modules:
            del sys.modules[module_name]
        globals().pop(module_name, None)

    def _test_stcat(self, argv=None, incoming=None):
        """
        Helper function to pass stdin.
        """
        self._del_module()
        if argv is None:
            argv = ["stcat.py"]
        else:
            argv = ["stcat.py"] + argv
        with patch.object(
            sys, "argv", argv
        ), captured_stdout() as stdout, captured_stdin() as stdin:
            import stdisplay.stcat  # pylint: disable=import-outside-toplevel

            if incoming is not None:
                stdin.write(incoming)
            stdin.seek(0)
            stdisplay.stcat.main()
        result = stdout.getvalue()  # pylint: disable=no-member
        return result

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
                self.assertEqual(text, self._test_stcat(argv=argv))

    def test_stcat_stdin(self):
        """
        Test passing stdin.
        """
        self.assertEqual("", self._test_stcat())
        self.assertEqual("", self._test_stcat(incoming=""))
        self.assertEqual("", self._test_stcat(argv=["-"]))
        self.assertEqual(
            "Hello world", self._test_stcat(incoming="Hello world")
        )
        self.assertEqual(
            "Hello world",
            self._test_stcat(argv=["-"], incoming="Hello world"),
        )


if __name__ == "__main__":
    unittest.main()
