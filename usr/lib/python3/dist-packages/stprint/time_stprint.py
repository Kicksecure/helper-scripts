#!/usr/bin/env python3
# pylint: disable=missing-module-docstring

import timeit
from re import compile as re_compile, sub as re_sub
from typing import Optional
from sys import argv, stdin
from stprint.stprint import get_sgr_support, get_sgr_pattern


# pylint: disable=missing-function-docstring
def stprint_repl(
    untrusted_text: str,
    sgr: Optional[int] = get_sgr_support(),
    exclude_sgr: Optional[list[str]] = None,
) -> str:
    sgr_pattern = get_sgr_pattern(sgr=sgr, exclude_sgr=exclude_sgr)
    sgr_pattern = r"(\x1b(?!\[" + sgr_pattern + r")|[^\x1b\n\t\x20-\x7E])"
    return str(re_sub(re_compile(sgr_pattern), "_", untrusted_text))


UNTRUSTED_TEXT = ""
if len(argv) > 1:
    UNTRUSTED_TEXT = "".join(argv[1:])
else:
    UNTRUSTED_TEXT = stdin.buffer.read().decode("ascii", errors="ignore")


# pylint: disable=missing-function-docstring
def main() -> None:
    def timer_listgen() -> float:
        return timeit.timeit(
            "stprint(UNTRUSTED_TEXT)",
            setup="from stprint import stprint",
            globals=globals(),
            number=rounds,
        )

    def timer_repl() -> float:
        return timeit.timeit(
            "stprint_repl(UNTRUSTED_TEXT)",
            setup="from __main__ import stprint_repl",
            globals=globals(),
            number=rounds,
        )

    rounds = 1000
    print(f"rounds: {rounds}")
    print(f"char length: {len(UNTRUSTED_TEXT)}")

    t_listgen = timer_listgen()
    t_repl = timer_repl()

    print(f"avg lgen time: {t_listgen:.6f} ms")
    print(f"avg repl time: {t_repl:.6f} ms")


if __name__ == "__main__":
    main()
