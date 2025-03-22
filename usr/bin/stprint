#!/usr/bin/env python3

## SPDX-FileCopyrightText: 2025 Benjamin Grande M. S. <ben.grande.b@gmail.com>
## SPDX-FileCopyrightText: 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
##
## SPDX-License-Identifier: AGPL-3.0-or-later

"""Safely print argument to stdout."""

from sys import argv, stdout
from stdisplay.stdisplay import stdisplay


def main() -> None:
    """Safely print argument to stdout."""
    if len(argv) > 1:
        untrusted_text = "".join(argv[1:])
        stdout.write(stdisplay(untrusted_text))
        stdout.flush()


if __name__ == "__main__":
    main()
