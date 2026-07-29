#!/usr/bin/python3 -Bsu

## Copyright (C) 2025 - 2025 Benjamin Grande M. S. <ben.grande.b@gmail.com>
## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## style-ok: allow-non-ascii -- this suite asserts that non-ASCII input is
## stripped, so the fixtures must contain the bytes under test.

"""
Test the stdisplay module.
"""

import io
import os
import unittest
from unittest import mock
from typing import (
    Any,
)
from curses import error as curses_error
from stdisplay import stcat, stcatn, stsponge, sttee
from stdisplay.stdisplay import (
    exclude_pattern,
    get_sgr_support,
    stdisplay,
)

## This is split into a global so it can be used by sanitize_string.py's tests.
simple_escape_cases: list[tuple[str, str]] = [
    ("\a", "_"),
    ("\b", "_"),
    ("\t", "\t"),
    ("\n", "\n"),
    ("\v", "_"),
    ("\f", "_"),
    ("\r", "_"),
    ("\a\n\b\t\v\f\r", "_\n_\t___"),
    ("\0", "_"),
    ("\1", "_"),
    ("\u0061", "a"),
    ("\u00d6 or \u00f6", "_ or _"),
    ("Ö or ö", "_ or _"),
    ("\x1b]8;;", "_]8;;"),
    ("a\x1b]8;;b", "a_]8;;b"),
    ("a\x1b]8;;", "a_]8;;"),
    ("a\x1b] 8;;", "a_] 8;;"),
    ("a\x1b ]8;;", "a_ ]8;;"),
    ("\033", "_"),
    ("\033[", "_["),
    ("\x1b[2K", "_[2K"),
    ("\\x1b[2K", "\\x1b[2K"),
    ("zero\u200bwidth", "zero_width"),
    ("A\u202er", "A_r"),
    ("prefix\u202astack\u202cpostfix", "prefix_stack_postfix"),
    ("isolate\u2066ltr\u2069end", "isolate_ltr_end"),
    ("join\u200dhere", "join_here"),
    ("soft\u00adhyphen", "soft_hyphen"),
    ("byte\ufefforder", "byte_order"),
    ("object\ufffcreplacement", "object_replacement"),
    ("emoji\ufe0fselector", "emoji_selector"),
]


class TestSTDisplay(unittest.TestCase):
    """
    Test stdisplay
    """

    def assert_stdisplay(
        self, text: str, expected_result: str, **kwargs: Any
    ) -> None:
        """
        Assert that stdisplay returned the expected results.
        """
        result = stdisplay(text, **kwargs)
        self.assertEqual(result, expected_result)

    def run_stdisplay_cases(
        self, cases: list[tuple[str, str]], **kwargs: Any
    ) -> None:
        """
        Run cases with unittest.TestCase().subTest() for easy debugging.
        """
        for text, expected_result in cases:
            with self.subTest(text=text, expected_result=expected_result):
                self.assert_stdisplay(text, expected_result, **kwargs)

    def test_exclude_pattern(self) -> None:
        """
        Test if exclude patterns are created correctly.
        """
        cases = [
            (r"(0*(30|31))", ["31"], ["30"]),
            (r"(0*(3[0-7]))", ["30", "37"], ["31", "32", "36"]),
        ]
        for orig_pat, exclude_pat, match_pat in cases:
            for exc in exclude_pat:
                with self.subTest(
                    orig_pat=orig_pat, exc=exc, match_pat=match_pat
                ):
                    exclude_regex = exclude_pattern(orig_pat, [exc])
                    self.assertNotRegex(exc, exclude_regex)
            for item in match_pat:
                with self.subTest(
                    orig_pat=orig_pat, exclude_pat=exclude_pat, match=item
                ):
                    exclude_regex = exclude_pattern(orig_pat, exclude_pat)
                    self.assertRegex(item, exclude_regex)

    def test_stdisplay_strip(self) -> None:
        """
        Test if stripping whitespace characters is disabled.
        """
        cases = [
            (" \n\t ", " \n\t "),
            ("\n\t", "\n\t"),
            ("\ta\n", "\ta\n"),
            ("", ""),
        ]
        self.run_stdisplay_cases(cases)

    def test_stdisplay_esc(self) -> None:
        """
        Test ESC sequence.
        """
        self.run_stdisplay_cases(simple_escape_cases)

    def test_stdisplay_sgr(self) -> None:
        """
        Test with SGR.
        """
        cases = [
            ("\x1b[m", "\x1b[m"),
            ("\x1b[;m", "\x1b[;m"),
            ("\x1b[;;;m", "\x1b[;;;m"),
            ("\x1b[31m", "\x1b[31m"),
            ("\x1b[;31m", "\x1b[;31m"),
            ("\x1b[31;m", "\x1b[31;m"),
            ("\x1b[;31;m", "\x1b[;31;m"),
            ("\x1b[41;31m", "\x1b[41;31m"),
            ("\x1b[;41;31m", "\x1b[;41;31m"),
            ("\x1b[41;31;m", "\x1b[41;31;m"),
            ("\x1b[;41;31;m", "\x1b[;41;31;m"),
            ("\x1b[5;23;9m", "\x1b[5;23;9m"),
            ("\x1b[;;5;;;23;;;;9m", "\x1b[;;5;;;23;;;;9m"),
            ("\x1b[5;;;23;9;;m", "\x1b[5;;;23;9;;m"),
            ("\x1b[;;;;;5;23;9;;m", "\x1b[;;;;;5;23;9;;m"),
            ("\x1b[38;5;1m", "\x1b[38;5;1m"),
            ("\x1b[;38;5;1m", "\x1b[;38;5;1m"),
            ("\x1b[0;38;5;1m", "\x1b[0;38;5;1m"),
            ("\x1b[38;5;1;1m", "\x1b[38;5;1;1m"),
            ("\x1b[38;5;1;m", "\x1b[38;5;1;m"),
            ("\x1b[38;2;255;0;1m", "\x1b[38;2;255;0;1m"),
            ("\x1b[38;2;255;0;0;m", "\x1b[38;2;255;0;0;m"),
            ("\x1b[38;2;255;0;0;0m", "\x1b[38;2;255;0;0;0m"),
            ("\x1b[;38;2;255;0;0m", "\x1b[;38;2;255;0;0m"),
            ("\x1b[0;38;2;255;0;0m", "\x1b[0;38;2;255;0;0m"),
            ("\x1b[;38;2;255;0;0;1;38;5;1;m", "\x1b[;38;2;255;0;0;1;38;5;1;m"),
            ("\x1b[;38;5;1;1;38;5;2;38;5;3m", "\x1b[;38;5;1;1;38;5;2;38;5;3m"),
            ("\x1b[;0;1;2;m", "\x1b[;0;1;2;m"),
            ("\x1b[000001;000000000002;m", "\x1b[000001;000000000002;m"),
            (
                "\x1b[;0038;05;0001;000001;000038;005;00002;00038;05;0000003m",
                "\x1b[;0038;05;0001;000001;000038;005;00002;00038;05;0000003m",
            ),
        ]
        self.run_stdisplay_cases(cases, sgr=2**24)

    def test_stdisplay_sgr_no_color(self) -> None:
        """
        Test without color
        """
        cases = [
            ("\x1b[m", "_[m"),
            ("\x1b[31m", "_[31m"),
        ]
        for sgr in (-1, -256, 0, 7):
            self.run_stdisplay_cases(cases, sgr=sgr)

    def test_stdisplay_sgr_three_bit(self) -> None:
        """
        Test with SGR 3-bit.
        """
        cases = [
            ("\x1b[31m", "\x1b[31m"),
            ("\x1b[91m", "_[91m"),
            ("\x1b[4m", "_[4m"),
            ("\x1b[38;5;1m", "_[38;5;1m"),
            ("\x1b[38;2;255;0;1m", "_[38;2;255;0;1m"),
        ]
        self.run_stdisplay_cases(cases, sgr=2**3)

    def test_stdisplay_sgr_four_bit(self) -> None:
        """
        Test with SGR 4-bit.
        """
        cases = [
            ("\x1b[m", "\x1b[m"),
            ("\x1b[31m", "\x1b[31m"),
            ("\x1b[91m", "\x1b[91m"),
            ("\x1b[4m", "_[4m"),
            ("\x1b[38;5;1m", "_[38;5;1m"),
            ("\x1b[38;2;255;0;1m", "_[38;2;255;0;1m"),
        ]
        self.run_stdisplay_cases(cases, sgr=2**4)

    def test_stdisplay_sgr_eight_bit(self) -> None:
        """
        Test with SGR 88 colors and 8-bit.
        """
        cases = [
            ("\x1b[m", "\x1b[m"),
            ("\x1b[31m", "\x1b[31m"),
            ("\x1b[91m", "\x1b[91m"),
            ("\x1b[4m", "\x1b[4m"),
            ("\x1b[38;5;1m", "\x1b[38;5;1m"),
            ("\x1b[38;2;255;0;1m", "_[38;2;255;0;1m"),
        ]
        for sgr in (88, 2**8):
            self.run_stdisplay_cases(cases, sgr=sgr)

    def test_stdisplay_sgr_twenty_four_bit(self) -> None:
        """
        Test with SGR 24-bit.
        """
        cases = [
            ("\x1b[m", "\x1b[m"),
            ("\x1b[31m", "\x1b[31m"),
            ("\x1b[91m", "\x1b[91m"),
            ("\x1b[4m", "\x1b[4m"),
            ("\x1b[38;5;1m", "\x1b[38;5;1m"),
            ("\x1b[38:5:1m", "\x1b[38:5:1m"),
            ("\x1b[38:5:1;31m", "\x1b[38:5:1;31m"),
            ("\x1b[38;;5;1m", "_[38;;5;1m"),
            ("\x1b[38;5;;1m", "_[38;5;;1m"),
            ("\x1b[38;2;255;0;1m", "\x1b[38;2;255;0;1m"),
            ("\x1b[38:2:255:0:1m", "\x1b[38:2:255:0:1m"),
            ("\x1b[38:2:255:0:1;31m", "\x1b[38:2:255:0:1;31m"),
            ("\x1b[38;;2;255;0;1m", "_[38;;2;255;0;1m"),
            ("\x1b[38;2;;255;0;1m", "_[38;2;;255;0;1m"),
            ("\x1b[38;2;255;;0;1m", "_[38;2;255;;0;1m"),
            ("\x1b[38;2;255;0;;1m", "_[38;2;255;0;;1m"),
            ("\x1b[38;2:255:0:1m", "_[38;2:255:0:1m"),
            ("\x1b[38:2;255:0:1m", "_[38:2;255:0:1m"),
            ("\x1b[38:2:255;0:1m", "_[38:2:255;0:1m"),
            ("\x1b[38:2:255:0;1m", "_[38:2:255:0;1m"),
        ]
        self.run_stdisplay_cases(cases, sgr=2**24)

    def test_stdisplay_no_extra_sgr(self) -> None:
        """
        Test disabling extra SGR.
        """
        cases = [
            ("\x1b[31m", "\x1b[31m"),
            ("\x1b[38;5;1m", "_[38;5;1m"),
            ("\x1b[1;38;5;1;0m", "_[1;38;5;1;0m"),
            ("\x1b[38;2;255;0;0m", "_[38;2;255;0;0m"),
            ("\x1b[2;38;2;255;0;0;1m", "_[2;38;2;255;0;0;1m"),
        ]
        self.run_stdisplay_cases(
            cases, sgr=2**24, exclude_sgr=["0*[3-4]8;0*(2|5);.*"]
        )

    def test_stdisplay_no_sgr(self) -> None:
        """
        Test disabling SGR.
        """
        cases = [
            ("\x1b[31m", "_[31m"),
            ("\x1b[38;5;1m", "_[38;5;1m"),
            ("\x1b[1;38;5;1;0m", "_[1;38;5;1;0m"),
            ("\x1b[38;2;255;0;0m", "_[38;2;255;0;0m"),
            ("\x1b[2;38;2;255;0;0;1m", "_[2;38;2;255;0;0;1m"),
        ]
        self.run_stdisplay_cases(cases, sgr=-1)

    def test_stdisplay_no_specific_sgr(self) -> None:
        """
        Test disabling specific SGR.
        """
        cases = [
            ("\x1b[30m", "_[30m"),
            ("\x1b[000030m", "_[000030m"),
            ("\x1b[31m", "\x1b[31m"),
            ("\x1b[32m", "\x1b[32m"),
            ("\x1b[37m", "_[37m"),
            ("\x1b[30;1m", "_[30;1m"),
            ("\x1b[0;30m", "_[0;30m"),
            ("\x1b[38;5;30m", "\x1b[38;5;30m"),
            ("\x1b[0;;;30;;;38;5;0m", "_[0;;;30;;;38;5;0m"),
            ("\x1b[38;5;254m", "_[38;5;254m"),
            ("\x1b[38;5;10;38;2;50;253;90;0m", "_[38;5;10;38;2;50;253;90;0m"),
            ("\x1b[38;2;0;30;0m", "\x1b[38;2;0;30;0m"),
            ("\x1b[38;2;0;0;0;30m", "_[38;2;0;0;0;30m"),
            ("\x1b[30;38;2;0;0;0m", "_[30;38;2;0;0;0m"),
            ("\x1b[38;2;0;0;0;37;38;5;0m", "_[38;2;0;0;0;37;38;5;0m"),
            ("\x1b[38;2;0;0;0;;37;;38;5;0m", "_[38;2;0;0;0;;37;;38;5;0m"),
            (
                "\x1b[0038;002;000;000;000;;0037;;0038;005;000m",
                "_[0038;002;000;000;000;;0037;;0038;005;000m",
            ),
            ("\x1b[38;2;0;0;0;;36;;38;5;0m", "\x1b[38;2;0;0;0;;36;;38;5;0m"),
            ("\x1b[38;2;0;37;0;;36;;38;5;0m", "\x1b[38;2;0;37;0;;36;;38;5;0m"),
            ("\x1b[38;2;0;37;0;36;38;5;37m", "\x1b[38;2;0;37;0;36;38;5;37m"),
            ("\x1b[38;2;0;0;0;1;38;5;250;2m", "_[38;2;0;0;0;1;38;5;250;2m"),
            ("\x1b[38;2;10;253;90m", "_[38;2;10;253;90m"),
        ]
        exclude_sgr = [
            "0*30",
            "0*37",
            "0*38;0*5;0*25[0-4]",
            r"0*38;0*2;\d+;0*253;\d+",
        ]
        self.run_stdisplay_cases(cases, sgr=2**24, exclude_sgr=exclude_sgr)

    def test_non_sgr_escape_sequences(self) -> None:
        """
        Ensure sequences outside the SGR allowlist are neutralized.
        """

        cases = [
            ("\x1b]0;evil title\x07", "_]0;evil title_"),
            ("\x1bP1;2|malicious\x1b\\", "_P1;2|malicious_\\"),
            ("\x1b_Gf=24,s=1,v=1;AAAA\x1b\\", "__Gf=24,s=1,v=1;AAAA_\\"),
            ("\x1b%Gpayload", "_%Gpayload"),
            ("\u009b31mnot-sgr", "_31mnot-sgr"),
            ("\x1b_application command\x1b\\", "__application command_\\"),
            ("\x1b^privacy message\x1b\\", "_^privacy message_\\"),
            ("\x1bXsave me\x1b\\", "_Xsave me_\\"),
            ("\u009fstate\u009c", "_state_"),
            ("\u0084wrap\u008d", "_wrap_"),
            ("\u009dhard-title\u009c", "_hard-title_"),
            ("\u0090capture\u009c", "_capture_"),
            ("\u0098privacy\u009c", "_privacy_"),
            ("\u0091safe\u009c", "_safe_"),
            ("\u0085hard\u008a", "_hard_"),
            ("\u0080pad\u008f", "_pad_"),
            ("\u0092status\u0097", "_status_"),
            ("visible\x0eshift\x0f", "visible_shift_"),
            ("erase\x18me\x1a", "erase_me_"),
            ("units\x1cgroup\x1f", "units_group_"),
            ("\x1b]52;;\x1b]0;X\x07", "_]52;;_]0;X_"),
            ("\x1b]52;c;clip\x07", "_]52;c;clip_"),
            ("\x1bPqpayload\x07", "_Pqpayload_"),
            ("\x1bP2$tight\x1b\\", "_P2$tight_\\"),
        ]
        self.run_stdisplay_cases(cases, sgr=2**24)


class TestSTDisplayClis(unittest.TestCase):
    """
    Tests for the stcat / stcatn / stsponge / sttee entry points.

    These modules do 'from sys import argv, stdin, stdout', binding at import,
    so the MODULE attributes are patched rather than sys.*. Nothing drove them
    before, which is why their stdin and no-stdin branches were unreached.
    """

    @staticmethod
    def _text_in(content: str) -> io.TextIOWrapper:
        """A readable stdin carrying content."""

        buffer: io.TextIOWrapper = io.TextIOWrapper(
            io.BytesIO(content.encode("utf-8")), encoding="utf-8", newline="\n"
        )
        return buffer

    @staticmethod
    def _text_out() -> tuple[io.TextIOWrapper, io.BytesIO]:
        """A writable stdout plus the buffer behind it."""

        raw: io.BytesIO = io.BytesIO()
        return (
            io.TextIOWrapper(raw, encoding="utf-8", newline="\n"),
            raw,
        )

    def _run(
        self, module: object, args: list[str], stdin_text: str | None
    ) -> str:
        """Drive a CLI module's main() and return what it wrote."""

        out_stream, raw = self._text_out()
        stdin_stream = (
            None if stdin_text is None else self._text_in(stdin_text)
        )
        with (
            mock.patch.object(module, "argv", ["prog", *args]),
            mock.patch.object(module, "stdout", out_stream),
            mock.patch.object(module, "stdin", stdin_stream),
        ):
            module.main()  # type: ignore[attr-defined]
        out_stream.flush()
        return raw.getvalue().decode("utf-8")

    def test_stcat_reads_stdin_with_no_arguments(self) -> None:
        """No argument means read stdin, sanitizing as it goes."""

        ## BEL is redacted at every colour depth, unlike an SGR colour code,
        ## which stdisplay preserves when the terminal supports it.
        output: str = self._run(stcat, [], "a\x07b\n")

        self.assertEqual(output, "a_b\n")

    def test_stcat_dash_argument_reads_stdin(self) -> None:
        """'-' names stdin explicitly."""

        output: str = self._run(stcat, ["-"], "x\x07y\n")

        self.assertEqual(output, "x_y\n")

    def test_stcat_without_stdin_writes_nothing(self) -> None:
        """stdin can be None; that is not a crash."""

        self.assertEqual(self._run(stcat, [], None), "")

    def test_stcatn_trims_and_terminates_each_line(self) -> None:
        """stcatn trims trailing whitespace and guarantees a final newline."""

        output: str = self._run(stcatn, [], "keep   \nsecond\t\n")

        self.assertEqual(output, "keep\nsecond\n")

    def test_stcatn_dash_argument_reads_stdin(self) -> None:
        """'-' names stdin for stcatn too."""

        self.assertEqual(self._run(stcatn, ["-"], "v   \n"), "v\n")

    def test_stcatn_without_stdin_writes_nothing(self) -> None:
        """stdin None is handled rather than dereferenced."""

        self.assertEqual(self._run(stcatn, [], None), "")

    def test_stsponge_and_sttee_read_stdin(self) -> None:
        """
        Both soak up stdin; neither had its stdin branch executed before.
        """

        self.assertIn("a_b", self._run(stsponge, [], "a\x07b\n"))
        self.assertIn("c_d", self._run(sttee, [], "c\x07d\n"))

    def test_stsponge_and_sttee_without_stdin(self) -> None:
        """stdin None must be handled, not dereferenced."""

        self.assertEqual(self._run(stsponge, [], None), "")
        self.assertEqual(self._run(sttee, [], None), "")

    def test_multiple_arguments_are_all_processed(self) -> None:
        """
        The argument loop must iterate. With one argument it never takes its
        back edge, so a second '-' is what proves each argument is handled
        rather than only the first. The second read sees an exhausted stdin.
        """

        self.assertEqual(self._run(stcat, ["-", "-"], "p\x07q\n"), "p_q\n")
        self.assertEqual(self._run(stcatn, ["-", "-"], "r\x07s   \n"), "r_s\n")

    def test_dash_arguments_with_no_stdin_are_skipped(self) -> None:
        """
        '-' names stdin, but stdin can be None. Each such argument is then
        skipped and the loop moves on, rather than dereferencing None.
        """

        self.assertEqual(self._run(stcat, ["-", "-"], None), "")
        self.assertEqual(self._run(stcatn, ["-", "-"], None), "")


class TestGetSgrSupport(unittest.TestCase):
    """
    get_sgr_support() reads the environment to decide how much colour is safe.
    Its branches are env-dependent, so they are driven explicitly rather than
    left to whatever the test runner happens to export.
    """

    def test_no_color_disables_everything(self) -> None:
        """NO_COLOR set at all means no SGR is permitted."""

        with mock.patch.dict(os.environ, {"NO_COLOR": "1"}, clear=True):
            self.assertEqual(get_sgr_support(), -1)

    def test_dumb_terminal_disables_everything(self) -> None:
        """TERM=dumb likewise."""

        with mock.patch.dict(os.environ, {"TERM": "dumb"}, clear=True):
            self.assertEqual(get_sgr_support(), -1)

    def test_truecolor_is_recognised(self) -> None:
        """COLORTERM=truecolor short-circuits the terminfo lookup."""

        for value in ("truecolor", "24bit", "TrueColor"):
            with mock.patch.dict(
                os.environ, {"COLORTERM": value, "TERM": "xterm"}, clear=True
            ):
                self.assertEqual(get_sgr_support(), 2**24)

    def test_terminfo_failure_falls_back(self) -> None:
        """
        An unusable terminfo database must not raise out of a display helper;
        it reports -2 so the caller redacts rather than guesses.
        """

        with (
            mock.patch.dict(os.environ, {"TERM": "xterm"}, clear=True),
            mock.patch(
                "stdisplay.stdisplay.setupterm", side_effect=curses_error()
            ),
        ):
            self.assertEqual(get_sgr_support(), -2)
