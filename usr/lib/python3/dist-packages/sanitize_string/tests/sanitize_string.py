#!/usr/bin/python3 -su

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

# pylint: disable=missing-module-docstring,fixme

from strip_markup.tests.strip_markup import TestStripMarkupBase
from stdisplay.tests.stdisplay import simple_escape_cases

from sanitize_string.sanitize_string import main as sanitize_string_main


class TestSanitizeString(TestStripMarkupBase):
    """
    Tests for sanitize_string.py.
    """

    maxDiff = None

    argv0: str = "sanitize-string"

    def test_help(self) -> None:
        """
        Ensure sanitize_string.py's help output is as expected.
        """

        help_str: str = """\
sanitize-string: Usage: sanitize-string [--help] max_length [string]
  If no string is provided as an argument, the string is read from standard input.
  Set max_length to 'nolimit' to allow arbitrarily long strings.
"""
        self._test_args(
            main_func=sanitize_string_main,
            argv0=self.argv0,
            stdout_string="",
            stderr_string=help_str,
            args=["--help"],
        )
        self._test_args(
            main_func=sanitize_string_main,
            argv0=self.argv0,
            stdout_string="",
            stderr_string=help_str,
            args=["-h"],
        )

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
                args=["nolimit", test_case[0]],
            )
            self._test_args(
                main_func=sanitize_string_main,
                argv0=self.argv0,
                stdout_string=test_case[1],
                stderr_string="",
                args=["--", "nolimit", test_case[0]],
            )
            self._test_stdin(
                main_func=sanitize_string_main,
                argv0=self.argv0,
                stdout_string=test_case[1],
                stderr_string="",
                stdin_string=test_case[0],
            )

    def test_malicious_case(self) -> None:
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
</body></html>
""",
                """\

__blowupWorld() __//__ Won't blow up world, because it's commented :) \
_[8mor not!_[0m

There really isn't bold text below, I promise!
_b_Not bold!_/b_

""",
            ),
        ]

        for test_case in test_case_list:
            self._test_args(
                main_func=sanitize_string_main,
                argv0=self.argv0,
                stdout_string=test_case[1],
                stderr_string="",
                args=["nolimit", test_case[0]],
            )
            self._test_args(
                main_func=sanitize_string_main,
                argv0=self.argv0,
                stdout_string=test_case[1],
                stderr_string="",
                args=["--", "nolimit", test_case[0]],
            )
            self._test_stdin(
                main_func=sanitize_string_main,
                argv0=self.argv0,
                stdout_string=test_case[1],
                stderr_string="",
                stdin_string=test_case[0],
            )
