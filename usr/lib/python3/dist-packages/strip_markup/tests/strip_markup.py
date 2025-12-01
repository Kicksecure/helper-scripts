#!/usr/bin/python3 -su

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

# pylint: disable=missing-module-docstring,fixme

import unittest
import sys
from io import StringIO
from typing import Callable
from unittest import mock
from strip_markup.strip_markup import main as strip_markup_main


class TestStripMarkupBase(unittest.TestCase):
    """
    Tests for strip_markup.py. Also reused by the tests for
    sanitize_string.py.
    """

    maxDiff = None

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def _test_args(
        self,
        main_func: Callable[[], int],
        argv0: str,
        stdout_string: str,
        stderr_string: str,
        args: list[str],
    ) -> None:
        """
        Executes the provided main function with the specified arguments, and
        ensures its output matches an expected value.
        """

        args_arr: list[str] = [argv0, *args]
        stdout_buf: StringIO = StringIO()
        stderr_buf: StringIO = StringIO()
        with (
            mock.patch.object(sys, "argv", args_arr),
            mock.patch.object(sys, "stdout", stdout_buf),
            mock.patch.object(sys, "stderr", stderr_buf),
        ):
            exit_code: int = main_func()
        self.assertEqual(stdout_buf.getvalue(), stdout_string)
        self.assertEqual(stderr_buf.getvalue(), stderr_string)
        self.assertEqual(exit_code, 0)
        stdout_buf.close()
        stderr_buf.close()

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def _test_stdin(
        self,
        main_func: Callable[[], int],
        argv0: str,
        stdout_string: str,
        stderr_string: str,
        stdin_string: str,
    ) -> None:
        """
        Executes the provided main function with the specified stdin, and
        ensures its output matches an expected value.
        """

        stdout_buf: StringIO = StringIO()
        stderr_buf: StringIO = StringIO()
        stdin_buf: StringIO = StringIO()
        stdin_buf.write(stdin_string)
        stdin_buf.seek(0)
        args_arr: list[str] = [argv0]
        with (
            mock.patch.object(sys, "argv", args_arr),
            mock.patch.object(sys, "stdin", stdin_buf),
            mock.patch.object(sys, "stdout", stdout_buf),
            mock.patch.object(sys, "stderr", stderr_buf),
        ):
            exit_code: int = main_func()
        self.assertEqual(stdout_buf.getvalue(), stdout_string)
        self.assertEqual(stderr_buf.getvalue(), stderr_string)
        self.assertEqual(exit_code, 0)
        stdout_buf.close()
        stderr_buf.close()
        stdin_buf.close()

    def _test_safe_strings(
        self,
        main_func: Callable[[], int],
        argv0: str,
        pos_args_prefix: list[str] | None = None,
    ) -> None:
        """
        Ensure strip_markup.py does not modify strings that contain no markup.
        This function is reused by sanitize_string's tests.
        """

        if pos_args_prefix is None:
            pos_args_prefix = []

        test_case_list_1: list[str] = [
            "safe",
            """\
This string is kinda long and has no newline at the end.""",
            """\
This string is kinda long and has a newline at the end.
""",
            """
This string is kinda long and has a newline at both the start and the end.
""",
            """\
This string is so long it may as well be an article. Embedded newlines make an
appearance here, as does a \t tab character. We'll throw in a bunch of symbols
for good measure: &#^*$&^%&!%#^&@%$R(*!_|:?}:"|}][',',./. And how about
25 numbers? 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
20, 21, 22, 23, 24, 25.

Of course, this example wouldn't be complete without a hard return. This is
probably long enough, so let's let this be the end of it.
""",
        ]
        for test_case in test_case_list_1:
            self._test_args(
                main_func=main_func,
                argv0=argv0,
                stdout_string=test_case,
                stderr_string="",
                args=[*pos_args_prefix, test_case],
            )
            self._test_args(
                main_func=main_func,
                argv0=argv0,
                stdout_string=test_case,
                stderr_string="",
                args=["--", *pos_args_prefix, test_case],
            )
            self._test_stdin(
                main_func=main_func,
                argv0=argv0,
                stdout_string=test_case,
                stderr_string="",
                stdin_string=test_case,
            )

        test_case_list_2: list[str] = [
            "--help",
            "-h",
        ]
        for test_case in test_case_list_2:
            self._test_args(
                main_func=main_func,
                argv0=argv0,
                stdout_string=test_case,
                stderr_string="",
                args=["--", *pos_args_prefix, test_case],
            )
            self._test_stdin(
                main_func=main_func,
                argv0=argv0,
                stdout_string=test_case,
                stderr_string="",
                stdin_string=test_case,
            )

    def _test_markup_strings(
        self,
        main_func: Callable[[], int],
        argv0: str,
        pos_args_prefix: list[str] | None = None,
    ) -> None:
        """
        Ensure strip_markup.py can strip markup from strings. This function is
        reused by sanitize_string's tests.
        """

        if pos_args_prefix is None:
            pos_args_prefix = []

        test_case_list: list[tuple[str, str]] = [
            (
                "<p>This is a small paragraph.</p>",
                "This is a small paragraph.",
            ),
            (
                "<p>This is a small paragraph with some <b>bold</b> text.</p>",
                "This is a small paragraph with some bold text.",
            ),
            (
                "<p>This is a weird paragraph that has no ending tag.",
                "This is a weird paragraph that has no ending tag.",
            ),
            (
                "<p>This is a <b>scrambled paragraph with tags in the wrong "
                + "order.</p></b>",
                "This is a scrambled paragraph with tags in the wrong order.",
            ),
            (
                """\
<html>
<head><script>alert("Gotcha!")</script></head>
<body>
<p>Hi! I'm an innocent paragraph, that certainly isn't part of a
document with an embedded script. :)</p>
</body>
</html>""",
                """\

alert("Gotcha!")

Hi! I'm an innocent paragraph, that certainly isn't part of a
document with an embedded script. :)

""",
            ),
            (
                "<huh>This is a document containing tags that don't really "
                + "exist.</huh>",
                "This is a document containing tags that don't really exist.",
            ),
        ]

        for test_case in test_case_list:
            self._test_args(
                main_func=main_func,
                argv0=argv0,
                stdout_string=test_case[1],
                stderr_string="",
                args=[*pos_args_prefix, test_case[0]],
            )
            self._test_args(
                main_func=main_func,
                argv0=argv0,
                stdout_string=test_case[1],
                stderr_string="",
                args=["--", *pos_args_prefix, test_case[0]],
            )
            self._test_stdin(
                main_func=main_func,
                argv0=argv0,
                stdout_string=test_case[1],
                stderr_string="",
                stdin_string=test_case[0],
            )

    def _test_malicious_markup_strings(
        self,
        main_func: Callable[[], int],
        argv0: str,
        pos_args_prefix: list[str] | None = None,
    ) -> None:
        """
        Ensure strip_markup.py can sanitize strings that contain additional
        markup after the first strip is completed. This function is reused by
        sanitize_string's tests.
        """

        if pos_args_prefix is None:
            pos_args_prefix = []

        # pylint: disable=line-too-long
        ## Examples of malicious strings pulled from the comments under
        ## https://stackoverflow.com/questions/753052/strip-html-from-strings-in-python
        ## TODO: Any better edge cases to throw at this?

        test_case_list: list[tuple[str, str]] = [
            (
                # pylint: disable=line-too-long
                ## https://stackoverflow.com/questions/753052/strip-html-from-strings-in-python#comment88388489_925630
                ## Posted by "AliBZ"
                "<<sc<script>script>alert(1)<</sc</script>/script>",
                "_script_alert(1)_/script_",
            ),
            (
                # pylint: disable=line-too-long
                ## https://stackoverflow.com/questions/753052/strip-html-from-strings-in-python#comment135427204_925630
                ## Posted by "Automatico"
                "<<b>b>Bold!<</b>/b>",
                "_b_Bold!_/b_",
            ),
            # (
            # pylint: disable=line-too-long
            ## https://stackoverflow.com/a/19730306/19474638
            ## Original source: https://www.mehmetince.net/django-strip_tags-bypass-vulnerability-exploit/
            ## Disabled because this no longer strips into unsafe HTML
            ## with Python 3.13.
            # "<img<!-- --> src=x onerror=alert(1);//><!-- -->",
            # "_img src=x onerror=alert(1);//_",
            # ),
        ]

        for test_case in test_case_list:
            self._test_args(
                main_func=main_func,
                argv0=argv0,
                stdout_string=test_case[1],
                stderr_string="",
                args=[*pos_args_prefix, test_case[0]],
            )
            self._test_args(
                main_func=main_func,
                argv0=argv0,
                stdout_string=test_case[1],
                stderr_string="",
                args=["--", *pos_args_prefix, test_case[0]],
            )
            self._test_stdin(
                main_func=main_func,
                argv0=argv0,
                stdout_string=test_case[1],
                stderr_string="",
                stdin_string=test_case[0],
            )


class TestStripMarkup(TestStripMarkupBase):
    """
    Tests specific to strip_markup.py.
    """

    argv0: str = "strip-html"

    def test_help(self) -> None:
        """
        Ensures strip_markup.py's help output is as expected.
        """

        help_str: str = """\
strip-html: Usage: strip-html [--help] [string]
  If no string is provided as an argument, the string is read from standard \
input.
"""
        self._test_args(
            main_func=strip_markup_main,
            argv0=self.argv0,
            stdout_string="",
            stderr_string=help_str,
            args=["--help"],
        )
        self._test_args(
            main_func=strip_markup_main,
            argv0=self.argv0,
            stdout_string="",
            stderr_string=help_str,
            args=["-h"],
        )

    def test_safe_strings(self) -> None:
        """
        Wrapper for _test_safe_strings specific to TestStripMarkup.
        """

        self._test_safe_strings(strip_markup_main, self.argv0)

    def test_markup_strings(self) -> None:
        """
        Wrapper for _test_markup_strings specific to TestStripMarkup.
        """

        self._test_markup_strings(strip_markup_main, self.argv0)

    def test_malicious_markup_strings(self) -> None:
        """
        Wrapper for _test_malicious_markup_strings specific to TestStripMarkup.
        """

        self._test_malicious_markup_strings(strip_markup_main, self.argv0)
