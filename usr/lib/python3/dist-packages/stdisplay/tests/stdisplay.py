#!/usr/bin/env python3

"""
Test the stdisplay module.
"""

import unittest
from typing import (
    Any,
)
from stdisplay.stdisplay import (
    exclude_pattern,
    stdisplay,
)


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
        cases = [
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
        ]
        self.run_stdisplay_cases(cases)

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


if __name__ == "__main__":
    unittest.main()
