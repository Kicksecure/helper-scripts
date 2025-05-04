#!/usr/bin/env python3  # pylint: disable=missing-module-docstring

import os
import shutil
import sys
import tempfile
import unittest
import importlib
from unittest.mock import patch
from test.support import captured_stdout, captured_stdin


class TestST(unittest.TestCase):
    """
    Base class for testing safe terminal utilities.
    """

    def setUp(self):
        self.temp_files = []
        contents = ["a b\n", "c d"]
        i = 0
        self.temp_dir = tempfile.mkdtemp()
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
        shutil.rmtree(self.temp_dir)

    def _del_module(self):
        module_name = "stdisplay." + self.module  # pylint: disable=no-member
        if module_name in sys.modules:
            del sys.modules[module_name]
        globals().pop(module_name, None)

    def _test_util(self, argv=None, incoming=None):
        """
        Helper function to pass stdin.
        """
        self._del_module()
        if argv is None:
            argv = [self.module + ".py"]  # pylint: disable=no-member
        else:
            argv = [self.module + ".py"] + argv  # pylint: disable=no-member
        with patch.object(
            sys, "argv", argv
        ), captured_stdout() as stdout, captured_stdin() as stdin:
            module = importlib.import_module("stdisplay." + self.module)  # pylint: disable=no-member
            if incoming is not None:
                stdin.write(incoming)
            stdin.seek(0)
            module.main()
        result = stdout.getvalue()
        return result
