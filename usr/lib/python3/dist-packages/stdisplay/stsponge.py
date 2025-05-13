#!/usr/bin/env python3

## SPDX-FileCopyrightText: 2025 Benjamin Grande M. S. <ben.grande.b@gmail.com>
## SPDX-FileCopyrightText: 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
##
## SPDX-License-Identifier: AGPL-3.0-or-later

"""Safely print stdin to stdout or file."""

from sys import argv, stdin, stdout, modules
import shutil
from tempfile import NamedTemporaryFile
from stdisplay.stdisplay import stdisplay


def main() -> None:
    """Safely print stdin to stdout or file."""
    # https://github.com/pytest-dev/pytest/issues/4843
    if "pytest" not in modules:
        stdin.reconfigure(errors="ignore")  # type: ignore
    untrusted_text_list = []
    for untrusted_text in stdin:
        untrusted_text_list.append(untrusted_text)
    if len(argv) == 1:
        stdout.write(stdisplay("".join(untrusted_text_list)))
        stdout.flush()
    else:
        with NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write(stdisplay("".join(untrusted_text_list)))
            temp_file.flush()
        for file in argv[1:]:
            shutil.copy2(temp_file.name, file)
        temp_file.close()


if __name__ == "__main__":
    main()
