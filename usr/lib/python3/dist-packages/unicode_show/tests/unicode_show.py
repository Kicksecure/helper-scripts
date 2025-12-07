#!/usr/bin/python3 -su

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

# pylint: disable=missing-module-docstring

import unittest
import sys
import pty
import tempfile
import os
from typing import Callable
from io import BytesIO, FileIO, TextIOWrapper
from unittest import mock
from stdisplay.stdisplay import stdisplay
from unicode_show.unicode_show import main as unicode_show_main


class TestUnicodeShow(unittest.TestCase):
    """
    Tests for unicode_show.py.
    """

    maxDiff = None
    argv0 = "unicode-show"

    # pylint: disable=line-too-long
    ## Code duplication. Copied from usr/lib/python3/dist-packages/strip_markup/tests/strip_markup.py.
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def _test_args(
        self,
        main_func: Callable[[], int],
        argv0: str,
        stdout_string: str,
        stderr_string: str,
        exit_code: int,
        args: list[str],
    ) -> None:
        """
        Executes the provided main function with the specified arguments, and
        ensures its output matches an expected value.
        """

        args_arr: list[str] = [argv0, *args]
        stdout_buf_internal: BytesIO = BytesIO()
        stderr_buf_internal: BytesIO = BytesIO()
        stdout_buf: TextIOWrapper = TextIOWrapper(
            buffer=stdout_buf_internal,
            encoding="utf-8",
            newline="\n",
            errors="surrogateescape",
        )
        stderr_buf: TextIOWrapper = TextIOWrapper(
            buffer=stderr_buf_internal,
            encoding="utf-8",
            newline="\n",
            errors="surrogateescape",
        )
        with (
            mock.patch.object(sys, "argv", args_arr),
            mock.patch.object(sys, "stdout", stdout_buf),
            mock.patch.object(sys, "stderr", stderr_buf),
            mock.patch.object(sys, "stdin", None),
        ):
            ret_exit_code: int = main_func()
        stdout_buf.seek(0, 0)
        stderr_buf.seek(0, 0)
        self.assertEqual(stdout_buf.read(), stdout_string)
        self.assertEqual(stderr_buf.read(), stderr_string)
        self.assertEqual(ret_exit_code, exit_code)
        stdout_buf.close()
        stderr_buf.close()

    # pylint: disable=line-too-long
    ## Code duplication. Copied from usr/lib/python3/dist-packages/strip_markup/tests/strip_markup.py.
    ## Modified to support `exit_code` argument.
    # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
    def _test_stdin(
        self,
        main_func: Callable[[], int],
        argv0: str,
        stdout_string: str,
        stderr_string: str,
        exit_code: int,
        args: list[str],
        stdin_string: str,
    ) -> None:
        """
        Executes the provided main function with the specified stdin, and
        ensures its output matches an expected value.
        """

        stdout_buf_internal: BytesIO = BytesIO()
        stderr_buf_internal: BytesIO = BytesIO()
        stdin_buf_internal: BytesIO = BytesIO()
        stdout_buf: TextIOWrapper = TextIOWrapper(
            buffer=stdout_buf_internal,
            encoding="utf-8",
            newline="\n",
            errors="surrogateescape",
        )
        stderr_buf: TextIOWrapper = TextIOWrapper(
            buffer=stderr_buf_internal,
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
        stdin_buf.write(stdin_string)
        stdin_buf.seek(0, 0)
        args_arr: list[str] = [argv0, *args]
        with (
            mock.patch.object(sys, "argv", args_arr),
            mock.patch.object(sys, "stdin", stdin_buf),
            mock.patch.object(sys, "stdout", stdout_buf),
            mock.patch.object(sys, "stderr", stderr_buf),
        ):
            ret_exit_code: int = main_func()
        stdout_buf.seek(0, 0)
        stderr_buf.seek(0, 0)
        self.assertEqual(stdout_buf.read(), stdout_string)
        self.assertEqual(stderr_buf.read(), stderr_string)
        self.assertEqual(ret_exit_code, exit_code)
        stdout_buf.close()
        stderr_buf.close()
        stdin_buf.close()

    def _test_stdin_pty(
        self,
        main_func: Callable[[], int],
        argv0: str,
        stdout_string: str,
        exit_code: int,
        args: list[str],
        stdin_string: str,
    ) -> None:
        """
        Executes the provided main function with the specified stdin via a
        PTY, and ensures its output matches an expected value.
        """

        master_pty_fd: int
        slave_pty_fd: int
        master_pty_fd, slave_pty_fd = pty.openpty()
        master_pty_stream: FileIO = FileIO(master_pty_fd, "r+")
        slave_pty_stream: FileIO = FileIO(slave_pty_fd, "r+")
        master_buf: TextIOWrapper = TextIOWrapper(
            buffer=master_pty_stream,
            encoding="utf-8",
            newline="\n",
            errors="surrogateescape",
        )
        slave_buf: TextIOWrapper = TextIOWrapper(
            buffer=slave_pty_stream,
            encoding="utf-8",
            newline="\n",
            errors="surrogateescape",
        )
        master_buf.write(stdin_string)
        ## EOF character, so that sanitize-string knows no further input will
        ## come from stdin
        master_buf.write("\x04")
        master_buf.flush()
        args_arr: list[str] = [argv0, *args]
        with (
            mock.patch.object(sys, "argv", args_arr),
            mock.patch.object(sys, "stdin", slave_buf),
            mock.patch.object(sys, "stdout", master_buf),
            mock.patch.object(sys, "stderr", master_buf),
        ):
            ret_exit_code: int = main_func()
        ## EOF character, so that the test script can read everything written
        ## by unicode-show
        master_buf.write("\x04")
        master_buf.flush()
        self.assertEqual(slave_buf.read(), stdout_string)
        self.assertEqual(ret_exit_code, exit_code)
        master_pty_stream.close()
        slave_pty_stream.close()

    def _test_file(
        self,
        main_func: Callable[[], int],
        argv0: str,
        stdout_string: str,
        stderr_string: str,
        exit_code: int,
        file_contents: str,
        filename_prefix: str = "",
    ) -> None:
        """
        Executes the provided main function with a temporary file containing
        the specified contents passed as an argument, and ensures the output
        is as expected. Replaces a template in the stdout_string and
        stderr_string with the full path to the generated temp file.
        """

        with tempfile.NamedTemporaryFile(
            mode="w+",
            encoding="utf-8",
            newline="\n",
            errors="surrogateescape",
            prefix=filename_prefix,
            delete_on_close=False,
        ) as tmp:
            tmp.write(file_contents)
            tmp.close()
            tmp_name_sanitized: str = stdisplay(tmp.name, sgr=-1)
            stdout_string = stdout_string.replace(
                "FILENAME_PLACEHOLDER", tmp_name_sanitized
            )
            stderr_string = stderr_string.replace(
                "FILENAME_PLACEHOLDER", tmp_name_sanitized
            )
            self._test_args(
                main_func=main_func,
                argv0=argv0,
                stdout_string=stdout_string,
                stderr_string=stderr_string,
                exit_code=exit_code,
                args=[tmp.name],
            )

    def test_ascii_control_characters(self) -> None:
        """
        Tests the detection of several ASCII control characters, including
        carriage returns.
        """

        test_cases: list[tuple[str, str, str]] = [
            ("\x00", "'\\x00'", "U+0000"),
            ("\x07", "'\\x07'", "U+0007"),
            ("\x1b", "'\\x1b'", "U+001B"),
            ("\r", "'\\r'", "U+000D"),
        ]
        for test_case in test_cases:
            input_str: str = f"start{test_case[0]}end\n"
            expect_str: str = f"""\
FILENAME_PLACEHOLDER:1: start[{test_case[2]}]end
   -> {test_case[1]} ({test_case[2]}, <unnamed>, Cc)
"""
            self._test_stdin(
                main_func=unicode_show_main,
                argv0=self.argv0,
                stdout_string=expect_str.replace(
                    "FILENAME_PLACEHOLDER", "<stdin>"
                ),
                stderr_string="",
                args=[],
                exit_code=1,
                stdin_string=input_str,
            )
            self._test_file(
                main_func=unicode_show_main,
                argv0=self.argv0,
                stdout_string=expect_str,
                stderr_string="",
                exit_code=1,
                file_contents=input_str,
            )

    def test_unicode_format_controls(self) -> None:
        """
        Tests the detections of Unicode characters used in Trojan Source
        attacks.
        """

        test_cases: list[tuple[str, str, str, str]] = [
            ("\u202a", "'\\u202a'", "U+202A", "LEFT-TO-RIGHT EMBEDDING"),
            ("\u202b", "'\\u202b'", "U+202B", "RIGHT-TO-LEFT EMBEDDING"),
            ("\u202d", "'\\u202d'", "U+202D", "LEFT-TO-RIGHT OVERRIDE"),
            ("\u202e", "'\\u202e'", "U+202E", "RIGHT-TO-LEFT OVERRIDE"),
            ("\u2066", "'\\u2066'", "U+2066", "LEFT-TO-RIGHT ISOLATE"),
            ("\u2067", "'\\u2067'", "U+2067", "RIGHT-TO-LEFT ISOLATE"),
            ("\u2068", "'\\u2068'", "U+2068", "FIRST STRONG ISOLATE"),
            ("\u202c", "'\\u202c'", "U+202C", "POP DIRECTIONAL FORMATTING"),
            ("\u2069", "'\\u2069'", "U+2069", "POP DIRECTIONAL ISOLATE"),
        ]
        for test_case in test_cases:
            input_str: str = f"pre{test_case[0]}post\n"
            expect_str: str = f"""\
FILENAME_PLACEHOLDER:1: pre[{test_case[2]}]post
   -> {test_case[1]} ({test_case[2]}, {test_case[3]}, Cf)
"""
            self._test_stdin(
                main_func=unicode_show_main,
                argv0=self.argv0,
                stdout_string=expect_str.replace(
                    "FILENAME_PLACEHOLDER", "<stdin>"
                ),
                stderr_string="",
                args=[],
                exit_code=1,
                stdin_string=input_str,
            )
            self._test_file(
                main_func=unicode_show_main,
                argv0=self.argv0,
                stdout_string=expect_str,
                stderr_string="",
                exit_code=1,
                file_contents=input_str,
            )

    def test_trailing_whitespace(self) -> None:
        """
        Tests the detection of trailing whitespace characters (tabs, newlines,
        and combinations of both)
        """

        test_cases: list[tuple[str, str]] = [
            (
                "Hello world! \n",
                """\
FILENAME_PLACEHOLDER:1: Hello world![U+0020]
   -> ' ' (U+0020, SPACE, Zs)
""",
            ),
            (
                "Hello world!\t\n",
                """\
FILENAME_PLACEHOLDER:1: Hello world![U+0009]
   -> '\\t' (U+0009, <unnamed>, Cc)
""",
            ),
            (
                "Hello world! \t\n",
                """\
FILENAME_PLACEHOLDER:1: Hello world![U+0020][U+0009]
   -> ' ' (U+0020, SPACE, Zs)
   -> '\\t' (U+0009, <unnamed>, Cc)
""",
            ),
            (
                "Hello world!\t \n",
                """\
FILENAME_PLACEHOLDER:1: Hello world![U+0009][U+0020]
   -> '\\t' (U+0009, <unnamed>, Cc)
   -> ' ' (U+0020, SPACE, Zs)
""",
            ),
        ]
        for test_case in test_cases:
            self._test_stdin(
                main_func=unicode_show_main,
                argv0=self.argv0,
                stdout_string=test_case[1].replace(
                    "FILENAME_PLACEHOLDER", "<stdin>"
                ),
                stderr_string="",
                args=[],
                exit_code=1,
                stdin_string=test_case[0],
            )
            self._test_file(
                main_func=unicode_show_main,
                argv0=self.argv0,
                stdout_string=test_case[1],
                stderr_string="",
                exit_code=1,
                file_contents=test_case[0],
            )

    def test_clean_ascii(self) -> None:
        """
        Tests if clean 7-bit ASCII passes without warnings.
        """

        test_string: str = (
            " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]"
            + "^_`abcdefghjiklmnopqrstuvwxyz{|}~\n"
        )
        self._test_stdin(
            main_func=unicode_show_main,
            argv0=self.argv0,
            stdout_string="",
            stderr_string="",
            args=[],
            exit_code=0,
            stdin_string=test_string,
        )
        self._test_file(
            main_func=unicode_show_main,
            argv0=self.argv0,
            stdout_string="",
            stderr_string="",
            exit_code=0,
            file_contents=test_string,
        )

    def test_invalid_utf8(self) -> None:
        """
        Tests if invalid Unicode is rejected with a fatal error.
        """

        ## \udcc3 = \xc3 encoded as a surrogate escape
        test_string: str = "valid line\n\udcc3"
        out_string: str = (
            "[ERROR] Unicode decode error [FILENAME_PLACEHOLDER]: 'utf-8' "
            + "codec can't decode byte 0xc3 in position 0: unexpected end of "
            + "data\n"
        )
        self._test_stdin(
            main_func=unicode_show_main,
            argv0=self.argv0,
            stdout_string="",
            stderr_string=out_string.replace("FILENAME_PLACEHOLDER", "stdin"),
            args=[],
            exit_code=2,
            stdin_string=test_string,
        )
        self._test_file(
            main_func=unicode_show_main,
            argv0=self.argv0,
            stdout_string="",
            stderr_string=out_string,
            exit_code=2,
            file_contents=test_string,
        )

    def test_pty_color(self) -> None:
        """
        Tests if unicode-show's color output can be controlled with the
        NOCOLOR and NO_COLOR environment variables.
        """

        test_string: str = "pre\u202apost\n"
        expect_string_color: str = """\
<stdin>:1: pre\033[91m[U+202A]\033[0mpost
   -> \033[96m'\\u202a' (U+202A, LEFT-TO-RIGHT EMBEDDING, Cf)\033[0m
"""
        expect_string_nocolor: str = """\
<stdin>:1: pre[U+202A]post
   -> '\\u202a' (U+202A, LEFT-TO-RIGHT EMBEDDING, Cf)
"""

        if "NOCOLOR" in os.environ:
            del os.environ["NOCOLOR"]
        if "NO_COLOR" in os.environ:
            del os.environ["NO_COLOR"]
        if "TERM" in os.environ:
            del os.environ["TERM"]
        self._test_stdin_pty(
            main_func=unicode_show_main,
            argv0=self.argv0,
            stdout_string=expect_string_color,
            exit_code=1,
            args=[],
            stdin_string=test_string,
        )

        os.environ["NOCOLOR"] = "y"
        self._test_stdin_pty(
            main_func=unicode_show_main,
            argv0=self.argv0,
            stdout_string=expect_string_nocolor,
            exit_code=1,
            args=[],
            stdin_string=test_string,
        )

        del os.environ["NOCOLOR"]
        os.environ["NO_COLOR"] = "1"
        self._test_stdin_pty(
            main_func=unicode_show_main,
            argv0=self.argv0,
            stdout_string=expect_string_nocolor,
            exit_code=1,
            args=[],
            stdin_string=test_string,
        )

        os.environ["NO_COLOR"] = "0"
        self._test_stdin_pty(
            main_func=unicode_show_main,
            argv0=self.argv0,
            stdout_string=expect_string_color,
            exit_code=1,
            args=[],
            stdin_string=test_string,
        )

    def test_unicode_in_filename(self) -> None:
        """
        Tests if Unicode characters in filenames are properly sanitized.
        """

        test_string: str = "pre\u202apost\n"
        expect_string: str = """\
FILENAME_PLACEHOLDER:1: pre[U+202A]post
   -> '\\u202a' (U+202A, LEFT-TO-RIGHT EMBEDDING, Cf)
"""
        self._test_file(
            main_func=unicode_show_main,
            argv0=self.argv0,
            stdout_string=expect_string,
            stderr_string="",
            exit_code=1,
            filename_prefix="danger\u202adanger",
            file_contents=test_string,
        )
