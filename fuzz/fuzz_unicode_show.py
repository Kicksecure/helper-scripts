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

## unicode_show.unicode_show uniquely does a cross-package absolute
## import (`from stdisplay.stdisplay import stdisplay`); the three
## sibling fuzz targets either only touch stdlib or use intra-package
## relative imports. Under PyInstaller's static analysis, wrapping
## that import in `with atheris.instrument_imports():` confuses the
## submodule discovery and the frozen binary fails at runtime with
## `ModuleNotFoundError: No module named 'unicode_show.unicode_show'`.
## atheris.instrument_all() (called at runtime in main()) is the
## documented alternative for cases the import-time instrumentation
## can't handle.
from unicode_show.unicode_show import describe_char, is_suspicious


def TestOneInput(data: bytes) -> None:
    fdp = atheris.FuzzedDataProvider(data)
    ## Don't use sys.maxsize here, it may try to allocate around 8 exabytes of
    ## random characters. 2 million and some characters is more than enough.
    s = fdp.ConsumeUnicodeNoSurrogates(2 ** 21)
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
    atheris.instrument_all()
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
