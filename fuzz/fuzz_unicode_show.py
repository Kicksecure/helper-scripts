#!/usr/bin/python3 -su

## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## AI-Assisted

"""
Atheris fuzz harness for unicode_show.

Exercises is_suspicious() and describe_char() on each character of
the fuzzed input. Both functions must:
  - never raise
  - return their declared types (bool / non-empty str)
"""

import atheris
import sys

with atheris.instrument_imports():
    from unicode_show.unicode_show import describe_char, is_suspicious


def TestOneInput(data: bytes) -> None:
    fdp = atheris.FuzzedDataProvider(data)
    s = fdp.ConsumeUnicodeNoSurrogates(sys.maxsize)
    for ch in s:
        if not isinstance(is_suspicious(ch), bool):
            raise RuntimeError(
                f"is_suspicious({ch!r}) did not return bool"
            )
        described = describe_char(ch)
        if not isinstance(described, str) or not described:
            raise RuntimeError(
                f"describe_char({ch!r}) returned non-str or empty: "
                f"{described!r}"
            )


def main() -> None:
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
