#!/usr/bin/python3 -su

## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## AI-Assisted

"""
Atheris fuzz harness for strip_markup.

Idempotency is the foundation of sanitize_string's documented
double-strip protection; this harness searches for inputs where
strip_markup(strip_markup(s)) != strip_markup(s).
"""

import atheris
import sys

with atheris.instrument_imports():
    from strip_markup.strip_markup_lib import strip_markup


def TestOneInput(data: bytes) -> None:
    fdp = atheris.FuzzedDataProvider(data)
    s = fdp.ConsumeUnicodeNoSurrogates(sys.maxsize)
    once = strip_markup(s)
    twice = strip_markup(once)
    if once != twice:
        raise RuntimeError(
            f"strip_markup not idempotent: input={s!r} once={once!r} "
            f"twice={twice!r}"
        )


def main() -> None:
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
