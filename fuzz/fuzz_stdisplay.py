#!/usr/bin/python3 -Bsu

## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## AI-Assisted

"""
Atheris fuzz harness for stdisplay.

stdisplay() takes a single str argument and must:
  - never raise on any input
  - be idempotent (output of one call equals output of two calls)

Both invariants are checked here so any input that triggers either
class of bug is reported as a fuzz finding.

Run locally:
    python3 -m atheris fuzz/fuzz_stdisplay.py

Run with a time budget:
    python3 -m atheris fuzz/fuzz_stdisplay.py -max_total_time=300

CI: invoked by .github/workflows/fuzz.yml, also used by
ClusterFuzzLite (.clusterfuzzlite/build.sh).
"""

import atheris
import sys

with atheris.instrument_imports():
    from stdisplay.stdisplay import stdisplay


def TestOneInput(data: bytes) -> None:
    fdp = atheris.FuzzedDataProvider(data)
    ## Don't use sys.maxsize here, it may try to allocate around 8 exabytes of
    ## random characters. 2 million and some characters is more than enough.
    s = fdp.ConsumeUnicodeNoSurrogates(2 ** 21)
    once = stdisplay(s)
    twice = stdisplay(once)
    if once != twice:
        raise RuntimeError(
            f"stdisplay not idempotent: input={s!r} once={once!r} twice={twice!r}"
        )


def main() -> None:
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
