#!/usr/bin/python3 -Bsu

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

# pylint: disable=missing-module-docstring,fixme,unknown-option-value

import os
import subprocess
import sys

from io import BytesIO, StringIO, TextIOWrapper
from unittest import mock

from strip_markup.tests.strip_markup import TestStripMarkupBase
from stdisplay.tests.stdisplay import simple_escape_cases

import sanitize_string.sanitize_string as sanitize_string_module
from sanitize_string.sanitize_string import main as sanitize_string_main


class TestSanitizeString(TestStripMarkupBase):
    """
    Tests for sanitize_string.py.
    """

    maxDiff = None

    argv0: str = "sanitize-string"
    help_str: str = """\
sanitize-string: Strip / sanitize dangerous control characters and markup.
Usage: sanitize-string [--help|-h] [--no-block] [--no-usage] [--newline] [--] max_length [string]

Arguments:
  --help|-h   Prints this help message.
  --no-block  When reading from stdin, sanitize line by line rather than
              buffering all input first. The string must not be provided as an
              argument if this option is specified. Note that this option may
              cause neutralized HTML to appear in sanitize-string's output
              that would have been stripped otherwise.
  --no-usage  If an error occurs when parsing arguments, do not print usage
              information.
  --newline   Append a new line to the output.
  --          End-of-options marker.
  max_length  Maximum allowable number of output characters, input will be
              truncated past this point. Set to 'nolimit' to allow arbitrarily
              long strings.
  string      The string to sanitize. If omitted, the string is read from
              standard input.
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

    def test_noblock_max_length(self) -> None:
        """
        Ensure that in --no-block mode, no further line is read once max_length
        is reached.
        """

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
        stdin_buf.write("123456\nsecond line\n")
        stdin_buf.seek(0, 0)

        with (
            mock.patch.object(
                sys, "argv", [self.argv0, "--no-block", "--", "5"]
            ),
            mock.patch.object(sys, "stdin", stdin_buf),
            mock.patch.object(sys, "stdout", stdout_buf),
        ):
            exit_code: int = sanitize_string_main()

        stdout_buf.seek(0, 0)
        self.assertEqual(stdout_buf.read(), "12345")
        self.assertEqual(exit_code, 0)

        ## The second line must still be waiting, unread.
        self.assertEqual(stdin_buf.read(), "second line\n")

    def test_broken_pipe(self) -> None:
        """
        Ensure a closed downstream ends the run cleanly rather than raising.
        """

        stdin_buf: TextIOWrapper = TextIOWrapper(
            buffer=BytesIO(), encoding="utf-8", newline="\n"
        )
        stdin_buf.write("first\nsecond\n")
        stdin_buf.seek(0, 0)

        class BrokenPipeStdout(StringIO):
            """
            A stdout whose every write reports the reader is gone.
            """

            def reconfigure(self, **kwargs: object) -> None:
                """
                Accept the encoding setup main() performs on stdout.
                """

            def write(self, *args: object, **kwargs: object) -> int:
                """
                Cause write attempts to fail.
                """

                raise BrokenPipeError()

        closed_stdout = BrokenPipeStdout()
        exit_code: int

        ## Normal, all-at-end write
        with (
            mock.patch.object(sys, "argv", [self.argv0, "nolimit"]),
            mock.patch.object(sys, "stdin", stdin_buf),
            mock.patch.object(sys, "stdout", closed_stdout),
        ):
            exit_code = sanitize_string_main()
        self.assertEqual(exit_code, 0)

        stdin_buf.seek(0, 0)

        ## Line-by-line write
        with (
            mock.patch.object(
                sys, "argv", [self.argv0, "--no-block", "--", "nolimit"]
            ),
            mock.patch.object(sys, "stdin", stdin_buf),
            mock.patch.object(sys, "stdout", closed_stdout),
        ):
            exit_code = sanitize_string_main()
        self.assertEqual(exit_code, 0)

    def test_zero_limit_still_appends_newline(self) -> None:
        """
        A zero max-length emits no sanitized content, but '--newline' must
        still append its newline, consistently with every other limit (the
        zero-limit fast path must not swallow it).
        """

        outbuf: BytesIO = BytesIO()
        stdout_buf: TextIOWrapper = TextIOWrapper(
            buffer=outbuf, encoding="utf-8", newline="\n"
        )
        with (
            mock.patch.object(
                sys, "argv", [self.argv0, "--newline", "--", "0", "content"]
            ),
            mock.patch.object(sys, "stdout", stdout_buf),
        ):
            exit_code: int = sanitize_string_main()
        stdout_buf.flush()
        self.assertEqual(outbuf.getvalue(), b"\n")
        self.assertEqual(exit_code, 0)

    def test_zero_limit_newline_does_not_read_stdin(self) -> None:
        """
        With '--no-block --newline' and a zero limit and no string argument,
        the newline must be emitted WITHOUT consuming stdin: a zero limit reads
        nothing.
        """

        stdin_buf: TextIOWrapper = TextIOWrapper(
            buffer=BytesIO(), encoding="utf-8", newline="\n"
        )
        stdin_buf.write("unread line\n")
        stdin_buf.seek(0, 0)
        outbuf: BytesIO = BytesIO()
        stdout_buf: TextIOWrapper = TextIOWrapper(
            buffer=outbuf, encoding="utf-8", newline="\n"
        )
        with (
            mock.patch.object(
                sys,
                "argv",
                [self.argv0, "--no-block", "--newline", "--", "0"],
            ),
            mock.patch.object(sys, "stdin", stdin_buf),
            mock.patch.object(sys, "stdout", stdout_buf),
        ):
            exit_code: int = sanitize_string_main()
        stdout_buf.flush()
        self.assertEqual(outbuf.getvalue(), b"\n")
        self.assertEqual(exit_code, 0)
        ## stdin must be untouched -- a zero limit consumes nothing.
        self.assertEqual(stdin_buf.read(), "unread line\n")

    def test_broken_pipe_no_shutdown_traceback(self) -> None:
        """
        A downstream that closes early must not leave a BrokenPipeError
        traceback from the interpreter's implicit stdout flush at shutdown.
        Runs the real CLI in a subprocess because that shutdown flush only
        happens on a genuine interpreter exit, which an in-process main() call
        cannot reproduce.
        """

        pkg_parent: str = os.path.dirname(
            os.path.dirname(os.path.abspath(sanitize_string_module.__file__))
        )
        env: dict[str, str] = dict(os.environ)
        existing: str = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = (
            pkg_parent + os.pathsep + existing if existing else pkg_parent
        )
        proc: subprocess.CompletedProcess[bytes] = subprocess.run(
            [
                "bash",
                "-c",
                'yes | "$0" -c "$1" --no-block -- nolimit | head -n 1',
                sys.executable,
                (
                    "import sys; "
                    + "from sanitize_string.sanitize_string import main; "
                    + "sys.exit(main())"
                ),
            ],
            env=env,
            capture_output=True,
            timeout=30,
            check=False,
        )
        self.assertNotIn(b"BrokenPipeError", proc.stderr)
        self.assertNotIn(b"Exception ignored", proc.stderr)

    def test_bare_double_dash(self) -> None:
        """
        Ensure '--' with nothing after it results in an error.
        """

        self._test_args(
            main_func=sanitize_string_main,
            argv0=self.argv0,
            stdout_string="",
            stderr_string=self.help_str,
            exit_code=1,
            args=["--"],
        )

    def test_no_argument_and_no_stdin(self) -> None:
        """
        Ensure sanitize-string exits 0 when given no string argument and stdin
        is closed.
        """

        with (
            mock.patch.object(sys, "argv", [self.argv0, "nolimit"]),
            mock.patch.object(sys, "stdin", None),
        ):
            exit_code: int = sanitize_string_main()

        self.assertEqual(exit_code, 0)

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
            (
                ## A raw ANSI escape sequence: the ESC byte becomes an
                ## underscore so a terminal cannot act on it; the rest is
                ## inert text.
                "\x1b[31mred\x1b[0m normal",
                "_[31mred_[0m normal",
            ),
            (
                ## Unicode bidirectional overrides (RIGHT-TO-LEFT OVERRIDE and
                ## POP DIRECTIONAL FORMATTING) that could reorder shown text
                ## are each replaced with an underscore.
                "before \N{RIGHT-TO-LEFT OVERRIDE} evil "
                + "\N{POP DIRECTIONAL FORMATTING} after",
                "before _ evil _ after",
            ),
            (
                ## Markup plus an escape: the tags are stripped and the ESC
                ## byte neutralized in the same pass.
                "<b>\x1b[8mhidden</b> shown",
                "_[8mhidden shown",
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
