#!/usr/bin/python3 -su

## Copyright (C) 2025 - 2025 Benjamin Grande M. S. <ben.grande.b@gmail.com>
## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

# pylint: disable=missing-module-docstring

import importlib
import os
import shutil
import sys
import tempfile
import unittest
from io import BytesIO, TextIOWrapper
from typing import Optional, Any
from unittest.mock import patch
from stdisplay.stdisplay import get_sgr_support


# pylint: disable=too-many-instance-attributes
class TestSTBase(unittest.TestCase):
    """
    Base class for testing safe terminal utilities.

    Assign "self.module" to the module you want to try on the "setup()" using
    "super()":

    >>> class TestSTCat(stdisplay.tests.TestSTBase):
    >>>     def setUp(self) -> None:
    >>>         self.module = "stcat"
    >>>         super().setUp()
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.text_dirty = "\x1b[0mTest\x1b[2Kor\x1b]1;is\x1b\n[m"
        self.text_dirty_sanitized = "\x1b[0mTest_[2Kor_]1;is_\n[m"
        self.text_malicious_unicode = """\
\N{RIGHT-TO-LEFT ISOLATE}\
\N{LEFT-TO-RIGHT ISOLATE}\
not commented\
\N{POP DIRECTIONAL ISOLATE}\
\N{LEFT-TO-RIGHT ISOLATE}\
//\
\N{POP DIRECTIONAL ISOLATE}\
\N{POP DIRECTIONAL ISOLATE} \
commented\x00after null\n\
"""
        self.text_malicious_unicode_sanitized = (
            "__not commented__//__ commented_after null\n"
        )
        super().__init__(*args, **kwargs)

    def setUp(self) -> None:
        self.module = "placeholder"
        self.tmpfiles_list = []
        contents = [b"a b\n", b"c d"]
        self.tmpdir = tempfile.mkdtemp()
        for i in range(0, 8):
            self.tmpfiles_list.append(os.path.join(self.tmpdir, str(i)))
            with open(self.tmpfiles_list[i], "wb") as file:
                if i == 0:
                    file.write(b"")
                elif i == 1:
                    file.write(b"".join(contents))
                elif i == 2:
                    file.write(b"".join(contents) + b"\n")
                elif i == 3:
                    file.write(self.text_dirty.encode(encoding="utf-8"))
                elif i in [4, 5]:
                    pass
                elif i == 6:
                    file.write(b"a\xffb\n")
                elif i == 7:
                    file.write(
                        self.text_malicious_unicode.encode(encoding="utf-8")
                    )
                file.flush()
                file.close()
        self.tmpfiles = {
            "empty": self.tmpfiles_list[0],
            "raw": self.tmpfiles_list[1],
            "newline": self.tmpfiles_list[2],
            "dirty": self.tmpfiles_list[3],
            "fill": self.tmpfiles_list[4],
            "fill2": self.tmpfiles_list[5],
            "invalid": self.tmpfiles_list[6],
            "malicious_unicode": self.tmpfiles_list[7],
        }

    def tearDown(self) -> None:
        shutil.rmtree(self.tmpdir)

    def _del_module(self) -> None:
        for module in ["stdisplay." + self.module]:
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
        stdout_buf_internal: BytesIO = BytesIO()
        stdin_buf_internal: BytesIO = BytesIO()
        stdout_buf: TextIOWrapper = TextIOWrapper(
            buffer=stdout_buf_internal,
            encoding="utf-8",
            newline="\n",
            errors="surrogateescape",
        )
        stdin_buf: TextIOWrapper = TextIOWrapper(
            buffer=stdin_buf_internal,
            encoding="utf-8",
            newline="\n",
            errors="surrogateescape",
        )
        if argv is None:
            argv = [self.module]
        else:
            argv = [self.module, *argv]
        if stdin is not None:
            stdin_buf.write(stdin)
            stdin_buf.seek(0, 0)
        with (
            patch.object(sys, "argv", argv),
            patch.object(sys, "stdin", stdin_buf),
            patch.object(sys, "stdout", stdout_buf),
        ):
            module = importlib.import_module("stdisplay." + self.module)
            module.main()
        stdout_buf.seek(0, 0)
        result = str(stdout_buf.read())  # pylint: disable=no-member
        stdout_buf.close()
        stdin_buf.close()
        return result
