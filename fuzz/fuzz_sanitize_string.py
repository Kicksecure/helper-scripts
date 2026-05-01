#!/usr/bin/python3 -su

## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## Authored by Claude (Anthropic).

"""
Atheris fuzz harness for sanitize_string.

Mirrors fuzz_stdisplay.py but on the composed sanitize_string()
(strip_markup + stdisplay). Idempotency is the documented "double-
strip protection" property; any failure here is a security regression.
"""

import atheris
import sys

with atheris.instrument_imports():
    from sanitize_string.sanitize_string_lib import sanitize_string


def TestOneInput(data: bytes) -> None:
    fdp = atheris.FuzzedDataProvider(data)
    s = fdp.ConsumeUnicodeNoSurrogates(sys.maxsize)
    once = sanitize_string(s)
    twice = sanitize_string(once)
    if once != twice:
        raise RuntimeError(
            f"sanitize_string not idempotent: input={s!r} once={once!r} "
            f"twice={twice!r}"
        )


def main() -> None:
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
