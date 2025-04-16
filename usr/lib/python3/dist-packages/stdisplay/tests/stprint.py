#!/usr/bin/env python3

"""
Test the stprint module.
"""

import os
import unittest
import subprocess
from stdisplay.stdisplay import (
    get_sgr_support,
)


class TestSTPrint(unittest.TestCase):
    """
    Test stprint
    """

    # pylint: disable=too-many-arguments
    def shell(
        self,
        text: str,
        *,
        stdin: bool = False,
        no_color: str = "",
        colorterm: str = "",
        term: str = "xterm-direct",
    ) -> subprocess.CompletedProcess[str]:
        """
        Run in a shell.
        """
        test_dir = os.path.dirname(os.path.abspath(__file__))
        script_dir = os.path.dirname(test_dir)
        command = "../../../../bin/stprint"
        input_data = ""
        if stdin:
            input_data = text
        else:
            command += f" '{text}'"
        ## Avoid tester environment from affecting tests, such as CI having
        ## TERM=dumb, but also allow us testing if RegEx is correct
        ## depending on the terminal provided.
        env = os.environ.copy()
        env.update(
            {"NO_COLOR": no_color, "COLORTERM": colorterm, "TERM": term}
        )

        os.environ.update({"NO_COLOR": "", "COLORTERM": "", "TERM": term})
        if get_sgr_support() < -1:
            self.fail(f"Terminfo entry not found: {term}")
        return subprocess.run(
            command,
            input=input_data,
            env=env,
            cwd=script_dir,
            shell=True,
            capture_output=True,
            check=True,
            text=True,
            timeout=2,
        )

    def test_stprint_main(self) -> None:
        """
        Test execution by the shell from standard input and parameter and if
        both methods of passing text match each other as well as matching the
        expected results.
        """
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
            ("\x1b[31m", "\x1b[31m"),
            ("\x1b[6m", "_[6m"),
        ]
        for text, expected_result in cases:
            with self.subTest(text=text, expected_result=expected_result):
                proc_param = self.shell(text, stdin=False)
                proc_stdin = self.shell(text, stdin=True)
                param_stdout = proc_param.stdout
                param_stderr = proc_param.stderr
                stdin_stdout = proc_stdin.stdout
                stdin_stderr = proc_stdin.stderr
                self.assertEqual(param_stderr, "")
                self.assertEqual(param_stdout, expected_result)
                self.assertEqual(stdin_stdout, "")
                self.assertEqual(param_stderr, stdin_stderr)

    def test_stprint_environment_sgr(self) -> None:
        """
        Test if environment variable can disable or enable SGR.
        """
        cases = [
            ("\x1b[31m", "_[31m"),
            ("\x1b[91m", "_[91m"),
            ("\x1b[4m", "_[4m"),
            ("\x1b[38;5;1;m", "_[38;5;1;m"),
            ("\x1b[38;2;255;0;1m", "_[38;2;255;0;1m"),
        ]
        for text, expected_result in cases:
            with self.subTest(text=text, expected_result=expected_result):
                result = self.shell(
                    text,
                    no_color="1",
                    colorterm="truecolor",
                    term="xterm-direct",
                )
                self.assertEqual(result.stdout, expected_result)

        cases = [
            ("\x1b[31m", "\x1b[31m"),
            ("\x1b[91m", "\x1b[91m"),
            ("\x1b[4m", "\x1b[4m"),
            ("\x1b[38;5;1;m", "\x1b[38;5;1;m"),
            ("\x1b[38;2;255;0;1m", "\x1b[38;2;255;0;1m"),
        ]
        for text, expected_result in cases:
            with self.subTest(text=text, expected_result=expected_result):
                result = self.shell(
                    text,
                    colorterm="truecolor",
                    term="xterm-old",
                )
                self.assertEqual(result.stdout, expected_result)

    def test_stprint_environment_term_sgr(self) -> None:
        """
        Test SGR being controlled by the $TERM environment variable.
        """
        cases = [
            ("\x1b[31m", "_[31m"),
            ("\x1b[91m", "_[91m"),
            ("\x1b[4m", "_[4m"),
            ("\x1b[38;5;1;m", "_[38;5;1;m"),
            ("\x1b[38;2;255;0;1m", "_[38;2;255;0;1m"),
        ]
        for text, expected_result in cases:
            with self.subTest(text=text, expected_result=expected_result):
                result = self.shell(text, term="xterm-old")
                self.assertEqual(result.stdout, expected_result)

        cases = [
            ("\x1b[31m", "\x1b[31m"),
            ("\x1b[91m", "_[91m"),
            ("\x1b[4m", "_[4m"),
            ("\x1b[38;5;1;m", "_[38;5;1;m"),
            ("\x1b[38;2;255;0;1m", "_[38;2;255;0;1m"),
        ]
        for text, expected_result in cases:
            with self.subTest(text=text, expected_result=expected_result):
                result = self.shell(text, term="xterm")
                self.assertEqual(result.stdout, expected_result)

        cases = [
            ("\x1b[31m", "\x1b[31m"),
            ("\x1b[91m", "\x1b[91m"),
            ("\x1b[4m", "_[4m"),
            ("\x1b[38;5;1;m", "_[38;5;1;m"),
            ("\x1b[38;2;255;0;1m", "_[38;2;255;0;1m"),
        ]
        for text, expected_result in cases:
            with self.subTest(text=text, expected_result=expected_result):
                result = self.shell(text, term="xterm-16color")
                self.assertEqual(result.stdout, expected_result)

        cases = [
            ("\x1b[31m", "\x1b[31m"),
            ("\x1b[91m", "\x1b[91m"),
            ("\x1b[4m", "\x1b[4m"),
            ("\x1b[38;5;1;m", "\x1b[38;5;1;m"),
            ("\x1b[38;2;255;0;1m", "_[38;2;255;0;1m"),
        ]
        for text, expected_result in cases:
            with self.subTest(text=text, expected_result=expected_result):
                for term in ("xterm-88color", "xterm-256color"):
                    result = self.shell(text, term=term)
                    self.assertEqual(result.stdout, expected_result)

        cases = [
            ("\x1b[31m", "\x1b[31m"),
            ("\x1b[91m", "\x1b[91m"),
            ("\x1b[4m", "\x1b[4m"),
            ("\x1b[38;5;1;m", "\x1b[38;5;1;m"),
            ("\x1b[38;2;255;0;1m", "\x1b[38;2;255;0;1m"),
        ]
        for text, expected_result in cases:
            with self.subTest(text=text, expected_result=expected_result):
                result = self.shell(text, term="xterm-direct")
                self.assertEqual(result.stdout, expected_result)


if __name__ == "__main__":
    unittest.main()
