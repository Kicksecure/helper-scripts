#!/usr/bin/env python3
"""
Test the stprint module.
"""

import os
import unittest
import subprocess
from typing import Any
from stprint.stprint import (
    exclude_pattern,
    stprint,
)


class TestSTPrint(unittest.TestCase):
    """
    Test stprint
    """

    def assert_stprint(
        self, text: str, expected_result: str, **kwargs: Any
    ) -> None:
        """
        Assert that stprint returned the expected results.
        """
        result = stprint(text, **kwargs)
        self.assertEqual(result, expected_result)

    def run_stprint_cases(
        self, cases: list[tuple[Any, str]], **kwargs: Any
    ) -> None:
        """
        Run cases with unittest.TestCase().subTest() for easy debugging.
        """
        for text, expected_result in cases:
            with self.subTest(text=text, expected_result=expected_result):
                self.assert_stprint(text, expected_result, **kwargs)

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
            for match in match_pat:
                with self.subTest(
                    orig_pat, exclude_pat=exclude_pat, match=match
                ):
                    exclude_regex = exclude_pattern(orig_pat, exclude_pat)
                    self.assertRegex(match, exclude_regex)

    def test_stprint_strip(self) -> None:
        """
        Test if stripping whitespace characters is disabled.
        """
        cases = [
            (" \n\t ", " \n\t "),
            ("\n\t", "\n\t"),
            ("\ta\n", "\ta\n"),
            ("", ""),
        ]
        self.run_stprint_cases(cases)

    def test_stprint_esc(self) -> None:
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
            ("\u00D6 or \u00F6", "_ or _"),
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
        self.run_stprint_cases(cases)

    def test_stprint_color(self) -> None:
        """
        Test with colors.
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
        self.run_stprint_cases(cases, colors=True, extra_colors=True)

    def test_stprint_no_extra_color(self) -> None:
        """
        Test disabling extra colors.
        """
        cases = [
            ("\x1b[31m", "\x1b[31m"),
            ("\x1b[38;5;1m", "_[38;5;1m"),
            ("\x1b[1;38;5;1;0m", "_[1;38;5;1;0m"),
            ("\x1b[38;2;255;0;0m", "_[38;2;255;0;0m"),
            ("\x1b[2;38;2;255;0;0;1m", "_[2;38;2;255;0;0;1m"),
        ]
        self.run_stprint_cases(cases, colors=True, extra_colors=False)

    def test_stprint_no_color(self) -> None:
        """
        Test disabling colors.
        """
        cases = [
            ("\x1b[31m", "_[31m"),
            ("\x1b[38;5;1m", "_[38;5;1m"),
            ("\x1b[1;38;5;1;0m", "_[1;38;5;1;0m"),
            ("\x1b[38;2;255;0;0m", "_[38;2;255;0;0m"),
            ("\x1b[2;38;2;255;0;0;1m", "_[2;38;2;255;0;0;1m"),
        ]
        self.run_stprint_cases(cases, colors=False, extra_colors=True)

    def test_stprint_no_specific_color(self) -> None:
        """
        Test disabling specific colors.
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
            ("\x1b[38;5;254m", "_[38;5;254m"),
            ("\x1b[38;2;0;0;0;1;38;5;250;2m", "_[38;2;0;0;0;1;38;5;250;2m"),
            ("\x1b[38;2;10;253;90m", "_[38;2;10;253;90m"),
            ("\x1b[38;5;10;38;2;50;253;90;0m", "_[38;5;10;38;2;50;253;90;0m"),
        ]
        exclude_colors = [
            "0*30",
            "0*37",
            "0*38;0*5;0*25[0-4]",
            r"0*38;0*2;\d+;0*253;\d+",
        ]
        self.run_stprint_cases(
            cases,
            colors=True,
            extra_colors=True,
            exclude_colors=exclude_colors,
        )

    def test_stprint_main(self) -> None:
        """
        Test execution by the shell from standard input and parameter and if
        both methods of passing text match each other as well as matching the
        expected results.
        """

        def shell(text: str, stdin: bool) -> subprocess.CompletedProcess[str]:
            test_dir = os.path.dirname(os.path.abspath(__file__))
            script_dir = os.path.dirname(test_dir)
            command = "./stprint.py"
            input_data = ""
            if stdin:
                input_data = text
            else:
                command += f" '{text}'"
            return subprocess.run(
                command,
                input=input_data,
                cwd=script_dir,
                shell=True,
                capture_output=True,
                check=True,
                text=True,
                timeout=2,
            )

        cases = [
            ("-h", "-h"),
            ("-?", "-?"),
            ("--help", "--help"),
            ("--helpabc", "--helpabc"),
            ("--help-abc", "--help-abc"),
            ("--whatever", "--whatever"),
            ("text", "text"),
            (" \n\t ", " \n\t "),
            ("\n\t", "\n\t"),
            ("\ta\n", "\ta\n"),
            ("", ""),
        ]
        for text, expected_result in cases:
            with self.subTest(text=text, expected_result=expected_result):
                proc_param = shell(text, stdin=False)
                proc_stdin = shell(text, stdin=True)
                param_stdout = proc_param.stdout
                param_stderr = proc_param.stderr
                stdin_stdout = proc_stdin.stdout
                stdin_stderr = proc_stdin.stderr
                self.assertEqual(param_stdout, expected_result)
                self.assertEqual(param_stderr, "")
                self.assertEqual(param_stdout, stdin_stdout)
                self.assertEqual(param_stderr, stdin_stderr)


if __name__ == "__main__":
    unittest.main()
