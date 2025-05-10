#!/usr/bin/env python3
# pylint: disable=missing-module-docstring

## SPDX-FileCopyrightText: 2025 Benjamin Grande M. S. <ben.grande.b@gmail.com>
## SPDX-FileCopyrightText: 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
##
## SPDX-License-Identifier: AGPL-3.0-or-later

import importlib
import os
import shutil
import sys
import tempfile
import unittest
from typing import Optional, Any
from test.support import captured_stdout, captured_stdin  # type: ignore
from unittest.mock import patch
from stdisplay.stdisplay import get_sgr_support


class TestSTBase(unittest.TestCase):
    """
    Base class for testing safe terminal utilities.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.text_dirty = "\x1b[0mTest\x1b[2Kor\x1b]1;is\x1b\n[m"
        self.text_dirty_sanitized = "\x1b[0mTest_[2Kor_]1;is_\n[m"
        super().__init__(*args, **kwargs)

    def setUp(self) -> None:
        self.tmpfiles_list = []
        contents = ["a b\n", "c d"]
        i = 0
        self.tmpdir = tempfile.mkdtemp()
        while i < 6:
            self.tmpfiles_list.append(os.path.join(self.tmpdir, str(i)))
            with open(self.tmpfiles_list[i], "w", encoding="utf-8") as file:
                if i == 0:
                    file.write("")
                elif i == 1:
                    file.write("".join(contents))
                elif i == 2:
                    file.write("".join(contents) + "\n")
                elif i == 3:
                    file.write(self.text_dirty)
                elif i in [4, 5]:
                    pass
                file.flush()
                file.close()
            i += 1
        self.tmpfiles = {
            "empty": self.tmpfiles_list[0],
            "raw": self.tmpfiles_list[1],
            "newline": self.tmpfiles_list[2],
            "dirty": self.tmpfiles_list[3],
            "fill": self.tmpfiles_list[4],
            "fill2": self.tmpfiles_list[5],
        }

    def tearDown(self) -> None:
        shutil.rmtree(self.tmpdir)

    def _del_module(self) -> None:
        for module in ["stdisplay." + self.module]:  # type: ignore # pylint: disable=no-member
            if module in sys.modules:
                del sys.modules[module]
            globals().pop(module, None)

    # pylint: disable=too-many-arguments
    def _test_util(
        self,
        argv: Optional[list[str]] = None,
        stdin: Optional[str] = None,
    ) -> str:
        """
        Helper function to pass stdin.
        """
        self._del_module()
        if argv is None:
            argv = [self.module + ".py"]  # type: ignore # pylint: disable=no-member
        else:
            argv = [self.module + ".py"] + argv  # type: ignore # pylint: disable=no-member
        with patch.object(
            sys, "argv", argv
        ), captured_stdout() as stdout, captured_stdin() as stdin_patch:
            module = importlib.import_module("stdisplay." + self.module)  # type: ignore # pylint: disable=no-member
            if stdin is not None:
                stdin_patch.write(stdin)
            stdin_patch.seek(0)
            module.main()
        result = str(stdout.getvalue())  # pylint: disable=no-member
        return result

    def _get_file(self, file: str) -> str:
        """
        Helper function get contents of a file.
        """
        with open(file, mode="r", encoding="utf-8") as fileobj:
            text = fileobj.read()
        return text
