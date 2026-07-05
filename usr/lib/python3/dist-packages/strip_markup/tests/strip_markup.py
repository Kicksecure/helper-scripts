#!/usr/bin/python3 -Bsu

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

# pylint: disable=missing-module-docstring,fixme,unknown-option-value

import sys
from io import BytesIO, TextIOWrapper
from typing import Callable
from unittest import TestCase, mock
from strip_markup.strip_markup import main as strip_markup_main


class TestStripMarkupBase(TestCase):
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

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def _test_stdin(
        self,
        main_func: Callable[[], int],
        argv0: str,
        stdout_string: str,
        stderr_string: str,
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
            exit_code: int = main_func()
        stdout_buf.seek(0, 0)
        stderr_buf.seek(0, 0)
        self.assertEqual(stdout_buf.read(), stdout_string)
        self.assertEqual(stderr_buf.read(), stderr_string)
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
for good measure: #^*$^%!%#^@%$R(*!_|:?}:"|}][',',./. And how about
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
                exit_code=0,
                args=[*pos_args_prefix, test_case],
            )
            self._test_args(
                main_func=main_func,
                argv0=argv0,
                stdout_string=test_case,
                stderr_string="",
                exit_code=0,
                args=["--", *pos_args_prefix, test_case],
            )
            self._test_stdin(
                main_func=main_func,
                argv0=argv0,
                stdout_string=test_case,
                stderr_string="",
                args=[*pos_args_prefix],
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
                exit_code=0,
                args=["--", *pos_args_prefix, test_case],
            )
            self._test_stdin(
                main_func=main_func,
                argv0=argv0,
                stdout_string=test_case,
                stderr_string="",
                args=[*pos_args_prefix],
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
            ## A '<' followed by whitespace then a tag name is not a tag to
            ## Python's html.parser, so it passes through verbatim - but a more
            ## lenient downstream parser (Qt's QTextDocument, used by
            ## msgcollector's generic_gui_message) skips the whitespace and
            ## revives the tag. The residual '<' must be neutered to '_' so the
            ## stripped output cannot be re-interpreted as markup.
            (
                "< a href='http://example.com'>click</a>",
                "_ a href='http://example.com'_click",
            ),
            (
                "< img src='http://example.com/beacon.png'>",
                "_ img src='http://example.com/beacon.png'_",
            ),
            ## Benign, non-markup '<', '>', and '&' characters are neutered to
            ## '_' as well. This is a deliberate, conservative choice:
            ## these characters can interact in surprising ways and trigger
            ## implementation-specific behavior in parsers. Guaranteeing they
            ## don't exist makes this provably safe against any downstream
            ## HTML parser.
            (
                "a < b",
                "a _ b",
            ),
            (
                "a > b",
                "a _ b",
            ),
            (
                "a & b",
                "a _ b",
            ),
            ## A tagless string containing '&' (e.g. any URL with a query
            ## string) must be sanitized, not completely removed. With
            ## convert_charrefs=True the parser buffers such text and only
            ## flushes it on close(); a missing close() used to drop the whole
            ## value, emptying the confirmation dialog. These guard that fix.
            (
                "http://example.com/?a=1&b=2",
                "http://example.com/?a=1_b=2",
            ),
            (
                "http://example.com/search?q=foo&lang=en&page=2",
                "http://example.com/search?q=foo_lang=en_page=2",
            ),
            (
                "http://example.com/?trailing=amp&",
                "http://example.com/?trailing=amp_",
            ),
        ]

        for test_case in test_case_list:
            self._test_args(
                main_func=main_func,
                argv0=argv0,
                stdout_string=test_case[1],
                stderr_string="",
                exit_code=0,
                args=[*pos_args_prefix, test_case[0]],
            )
            self._test_args(
                main_func=main_func,
                argv0=argv0,
                stdout_string=test_case[1],
                stderr_string="",
                exit_code=0,
                args=["--", *pos_args_prefix, test_case[0]],
            )
            self._test_stdin(
                main_func=main_func,
                argv0=argv0,
                stdout_string=test_case[1],
                stderr_string="",
                args=[*pos_args_prefix],
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
                exit_code=0,
                args=[*pos_args_prefix, test_case[0]],
            )
            self._test_args(
                main_func=main_func,
                argv0=argv0,
                stdout_string=test_case[1],
                stderr_string="",
                exit_code=0,
                args=["--", *pos_args_prefix, test_case[0]],
            )
            self._test_stdin(
                main_func=main_func,
                argv0=argv0,
                stdout_string=test_case[1],
                stderr_string="",
                args=[*pos_args_prefix],
                stdin_string=test_case[0],
            )


class TestStripMarkup(TestStripMarkupBase):
    """
    Tests specific to strip_markup.py.
    """

    argv0: str = "strip-markup"

    def test_help(self) -> None:
        """
        Ensures strip_markup.py's help output is as expected.
        """

        help_str: str = """\
strip-markup: Usage: strip-markup [--help] [string]
  If no string is provided as an argument, the string is read from standard \
input.
"""
        self._test_args(
            main_func=strip_markup_main,
            argv0=self.argv0,
            stdout_string="",
            stderr_string=help_str,
            exit_code=0,
            args=["--help"],
        )
        self._test_args(
            main_func=strip_markup_main,
            argv0=self.argv0,
            stdout_string="",
            stderr_string=help_str,
            exit_code=0,
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

    def test_bare_separator(self) -> None:
        """
        Ensure 'strip-markup --' with no positional argument following the
        separator falls back to reading stdin, rather than crashing with
        IndexError on arg_list[0].
        """

        ## With stdin available, '--' alone reads from stdin.
        self._test_stdin(
            main_func=strip_markup_main,
            argv0=self.argv0,
            stdout_string="hello",
            stderr_string="",
            args=["--"],
            stdin_string="hello",
        )

        ## With stdin closed, '--' alone exits cleanly with no output.
        self._test_args(
            main_func=strip_markup_main,
            argv0=self.argv0,
            stdout_string="",
            stderr_string="",
            exit_code=0,
            args=["--"],
        )
