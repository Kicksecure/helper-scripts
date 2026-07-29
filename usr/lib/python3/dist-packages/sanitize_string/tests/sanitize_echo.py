## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

# pylint: disable=missing-module-docstring,unknown-option-value

from strip_markup.tests.strip_markup import TestStripMarkupBase

from sanitize_string.sanitize_echo import main as sanitize_echo_main


class TestSanitizeEcho(TestStripMarkupBase):
    """
    Tests for sanitize_echo.py.
    """

    maxDiff = None

    argv0: str = "sanitize-echo"
    help_str: str = """\
sanitize-echo: Usage: sanitize-echo [--help] [--max-length LENGTH] [--] [string ...]
  Prints the sanitized string(s) followed by a newline.
  Multiple arguments are joined with a single space, as echo does.
  If no string is provided, it is read from standard input.
  LENGTH caps the sanitized output; 'nolimit' (the default) does not cap it.
"""

    def _expect(
        self,
        args: list[str],
        stdout_string: str,
        stderr_string: str = "",
        exit_code: int = 0,
    ) -> None:
        """
        Run sanitize-echo with args and assert its streams and exit code.
        """

        self._test_args(
            main_func=sanitize_echo_main,
            argv0=self.argv0,
            stdout_string=stdout_string,
            stderr_string=stderr_string,
            exit_code=exit_code,
            args=args,
        )

    def test_help(self) -> None:
        """
        Help goes to stderr and exits 0.
        """

        for test_arg in ("--help", "-h"):
            self._expect(
                args=[test_arg], stdout_string="", stderr_string=self.help_str
            )

    def test_trailing_newline(self) -> None:
        """
        Unlike sanitize-string, a newline is always appended -- that is the
        whole point of the echo shape.
        """

        self._expect(args=["plain"], stdout_string="plain\n")

    def test_empty_still_prints_newline(self) -> None:
        """
        No argument prints just the newline, as echo does.
        """

        self._expect(args=[""], stdout_string="\n")

    def test_arguments_joined_with_space(self) -> None:
        """
        Multiple arguments join with a single space.
        """

        self._expect(args=["a", "b", "c"], stdout_string="a b c\n")

    def test_escape_is_neutralized(self) -> None:
        """
        An ANSI sequence must not reach the terminal intact.
        """

        self._expect(
            args=["a\x1b[31mRED\x1b[0m"], stdout_string="a_[31mRED_[0m\n"
        )

    def test_carriage_return_cannot_forge_a_line(self) -> None:
        """
        A CR would let untrusted text overwrite what was already printed.
        """

        self._expect(args=["ok\rFAKE"], stdout_string="ok_FAKE\n")

    def test_markup_is_stripped(self) -> None:
        """
        sanitize-string's markup stripping is kept, which is what makes this
        stronger than stecho.
        """

        self._expect(args=["<b>bold</b>"], stdout_string="bold\n")

    def test_percent_is_literal(self) -> None:
        """
        The inline 'printf ... $(sanitize-string ...)' form this replaces
        treated the sanitized value as part of a FORMAT string, so a '%' in
        untrusted text was a conversion spec. Here it is data.
        """

        self._expect(args=["100% done %s"], stdout_string="100% done %s\n")

    def test_max_length_caps(self) -> None:
        """
        The cap applies to the sanitized text, and the newline still follows.
        """

        self._expect(
            args=["--max-length", "5", "abcdefghij"], stdout_string="abcde\n"
        )

    def test_nolimit_does_not_cap(self) -> None:
        """
        'nolimit' is the default and may also be passed explicitly.
        """

        self._expect(
            args=["--max-length", "nolimit", "abcdefghij"],
            stdout_string="abcdefghij\n",
        )

    def test_double_dash_ends_options(self) -> None:
        """
        A message starting with '-' survives after '--'.
        """

        self._expect(args=["--", "-n"], stdout_string="-n\n")

    def test_bad_max_length_is_rejected(self) -> None:
        """
        A non-numeric, negative, or missing cap is a usage error, not a
        silently ignored one.
        """

        for bad_args in (
            ["--max-length", "abc", "x"],
            ["--max-length", "-3", "x"],
            ["--max-length"],
        ):
            self._expect(
                args=bad_args,
                stdout_string="",
                stderr_string=self.help_str,
                exit_code=1,
            )
