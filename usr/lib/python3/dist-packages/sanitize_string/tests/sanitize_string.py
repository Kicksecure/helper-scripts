#!/usr/bin/python3 -Bsu

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

# pylint: disable=missing-module-docstring,fixme,unknown-option-value

import sys
from io import BytesIO, TextIOWrapper
from unittest import mock

from strip_markup.tests.strip_markup import TestStripMarkupBase
from stdisplay.tests.stdisplay import simple_escape_cases

from sanitize_string.sanitize_string import main as sanitize_string_main
from sanitize_string.sanitize_string_lib import sanitize_string


class TestSanitizeString(TestStripMarkupBase):
    """
    Tests for sanitize_string.py.
    """

    maxDiff = None

    argv0: str = "sanitize-string"
    help_str: str = """\
sanitize-string: Usage: sanitize-string [--help] max_length [string]
  If no string is provided as an argument, the string is read from standard input.
  Set max_length to 'nolimit' to allow arbitrarily long strings.
"""

    def test_help(self) -> None:
        """
        Ensure sanitize_string.py's help output is as expected.
        """

        for test_arg in ("--help", "-h"):
            self._test_args(
                main_func=sanitize_string_main,
                argv0=self.argv0,
                stdout_string="",
                stderr_string=self.help_str,
                exit_code=0,
                args=[test_arg],
            )

    def test_usage_errors(self) -> None:
        """
        Ensure argument validation errors emit usage and exit non-zero.
        """

        test_args_list: list[list[str]] = [
            [],
            ["-5"],
            ["not-a-number"],
            ["1", "2", "3"],
        ]

        for test_args in test_args_list:
            self._test_args(
                main_func=sanitize_string_main,
                argv0=self.argv0,
                stdout_string="",
                stderr_string=self.help_str,
                exit_code=1,
                args=test_args,
            )

    def test_stdin_matches_whole_input_for_multiline_markup(self) -> None:
        """
        Ensure sanitizing standard input as it arrives matches sanitizing the
        whole input at once when a markup construct spans a line boundary.
        Splitting such a construct would emit content the parser should have
        consumed, for instance the body of a multi-line comment.
        """

        multiline_input_list: list[str] = [
            "<!--\nsecret\n-->\n",
            "<div\nclass=x>text\n",
            "<scr\nipt>alert(1)</scr\nipt>\n",
            "before\n<!--\nhidden\n-->\nafter\n",
            "<a href=\n'x'>link</a>\n",
        ]

        for multiline_input in multiline_input_list:
            with self.subTest(multiline_input=multiline_input):
                self._test_stdin(
                    main_func=sanitize_string_main,
                    argv0=self.argv0,
                    stdout_string=sanitize_string(multiline_input),
                    stderr_string="",
                    args=["nolimit"],
                    stdin_string=multiline_input,
                )

    def test_stdin_stops_reading_once_budget_is_spent(self) -> None:
        """
        Ensure no further line is read once max_length is reached. Reading one
        more would block on a producer that is still running but has nothing
        left to emit, which defeats sanitizing standard input as it arrives.
        """

        stdin_buf_internal: BytesIO = BytesIO()
        stdin_buf: TextIOWrapper = TextIOWrapper(
            buffer=stdin_buf_internal, encoding="utf-8", newline="\n"
        )
        stdout_buf_internal: BytesIO = BytesIO()
        stdout_buf: TextIOWrapper = TextIOWrapper(
            buffer=stdout_buf_internal, encoding="utf-8", newline="\n"
        )
        stdin_buf.write("123456\nsecond line\n")
        stdin_buf.seek(0, 0)

        with (
            mock.patch.object(sys, "argv", [self.argv0, "5"]),
            mock.patch.object(sys, "stdin", stdin_buf),
            mock.patch.object(sys, "stdout", stdout_buf),
        ):
            exit_code: int = sanitize_string_main()

        stdout_buf.flush()
        self.assertEqual(exit_code, 0)
        self.assertEqual(
            stdout_buf_internal.getvalue().decode("utf-8"), "12345"
        )
        ## The second line must still be waiting, unread.
        self.assertEqual(stdin_buf.read(), "second line\n")

    def test_safe_strings(self) -> None:
        """
        Wrapper for _test_safe_strings (from TestStripMarkup) specific to
        TestSanitizeString.
        """

        self._test_safe_strings(
            sanitize_string_main, self.argv0, pos_args_prefix=["nolimit"]
        )

    def test_markup_strings(self) -> None:
        """
        Wrapper for _test_markup_strings (from TestStripMarkup) specific to
        TestSanitizeString.
        """

        self._test_markup_strings(
            sanitize_string_main, self.argv0, pos_args_prefix=["nolimit"]
        )

    def test_malicious_markup_strings(self) -> None:
        """
        Wrapper for _test_malicious_markup_strings (from TestStripMarkup)
        specific to TestSanitizeString.
        """

        self._test_malicious_markup_strings(
            sanitize_string_main, self.argv0, pos_args_prefix=["nolimit"]
        )

    def test_simple_escape_cases(self) -> None:
        """
        Ensures sanitize_string.py correctly sanitizes escape sequences and
        Unicode.
        """

        for test_case in simple_escape_cases:
            self._test_args(
                main_func=sanitize_string_main,
                argv0=self.argv0,
                stdout_string=test_case[1],
                stderr_string="",
                exit_code=0,
                args=["nolimit", test_case[0]],
            )
            self._test_args(
                main_func=sanitize_string_main,
                argv0=self.argv0,
                stdout_string=test_case[1],
                stderr_string="",
                exit_code=0,
                args=["--", "nolimit", test_case[0]],
            )
            self._test_stdin(
                main_func=sanitize_string_main,
                argv0=self.argv0,
                stdout_string=test_case[1],
                stderr_string="",
                args=["nolimit"],
                stdin_string=test_case[0],
            )

    def test_malicious_cases(self) -> None:
        """
        Ensures malicious HTML plus malicious Unicode plus malicious escape
        sequences are handled correctly.
        """

        ## TODO: Add more than one test case.

        test_case_list: list[tuple[str, str]] = [
            (
                """\
<html><head><script>
\N{RIGHT-TO-LEFT ISOLATE}\
\N{LEFT-TO-RIGHT ISOLATE}\
blowupWorld() \
\N{POP DIRECTIONAL ISOLATE}\
\N{LEFT-TO-RIGHT ISOLATE}\
//\
\N{POP DIRECTIONAL ISOLATE}\
\N{POP DIRECTIONAL ISOLATE} \
Won't blow up world, because it's commented :) \x1b[8mor not!\x1b[0m
</script></head><body>
<p>There really isn't bold text below, I promise!</p>
<<b>b>Not bold!<</b>/b>
<p>&#27;[8mThis text might become invisible.&#27;[0m</p>
</body></html>
""",
                """\

__blowupWorld() __//__ Won't blow up world, because it's commented :) \
_[8mor not!_[0m

There really isn't bold text below, I promise!
_b_Not bold!_/b_
[8mThis text might become invisible.[0m

""",
            ),
        ]

        for test_case in test_case_list:
            self._test_args(
                main_func=sanitize_string_main,
                argv0=self.argv0,
                stdout_string=test_case[1],
                stderr_string="",
                exit_code=0,
                args=["nolimit", test_case[0]],
            )
            self._test_args(
                main_func=sanitize_string_main,
                argv0=self.argv0,
                stdout_string=test_case[1],
                stderr_string="",
                exit_code=0,
                args=["--", "nolimit", test_case[0]],
            )
            self._test_stdin(
                main_func=sanitize_string_main,
                argv0=self.argv0,
                stdout_string=test_case[1],
                stderr_string="",
                args=["nolimit"],
                stdin_string=test_case[0],
            )

    def test_long_cases(self) -> None:
        """
        Ensures sanitize-string's truncation feature works.
        """

        test_case_list: list[tuple[str, str, str]] = [
            (
                "This is a longish string.",
                "9",
                "This is a",
            ),
            (
                "This is a longish string.",
                "15",
                "This is a longi",
            ),
            ("This is a longish string.", "100", "This is a longish string."),
            (
                "This is a longish string.",
                "0",
                "",
            ),
            (
                "<p>This string is shorter than it looks.</p>",
                "36",
                "This string is shorter than it looks",
            ),
            (
                "\x1b[8mThis text is hidden.\x1b[0m",
                "16",
                "_[8mThis text is",
            ),
            (
                """\
This text is multi-line.
That is, with a newline inserted.""",
                "42",
                """\
This text is multi-line.
That is, with a n""",
            ),
        ]

        for test_case in test_case_list:
            self._test_args(
                main_func=sanitize_string_main,
                argv0=self.argv0,
                stdout_string=test_case[2],
                stderr_string="",
                exit_code=0,
                args=[test_case[1], test_case[0]],
            )
            self._test_args(
                main_func=sanitize_string_main,
                argv0=self.argv0,
                stdout_string=test_case[2],
                stderr_string="",
                exit_code=0,
                args=["--", test_case[1], test_case[0]],
            )
            self._test_stdin(
                main_func=sanitize_string_main,
                argv0=self.argv0,
                stdout_string=test_case[2],
                stderr_string="",
                args=[test_case[1]],
                stdin_string=test_case[0],
            )
