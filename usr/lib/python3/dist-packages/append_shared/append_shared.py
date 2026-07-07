#!/usr/bin/python3 -Bsu

## Copyright (C) 2025 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

# pylint: disable=broad-exception-caught

"""
Unified implementation of 'append', 'append-once', and 'overwrite' tools.
"""

import sys
import os
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile


_executable_name: str = ""


def _print_usage() -> None:
    """
    Prints a brief usage message.
    """

    print(
        f"Usage: {_executable_name} /path/to/file 'content'",
        file=sys.stderr,
    )


def _print_info(info_msg: str) -> None:
    """
    Prints an informational message.
    """

    print(f"{_executable_name}: INFO: {info_msg}")


def _print_error(error_msg: str) -> None:
    """
    Prints an error message.
    """

    print(f"{_executable_name}: ERROR: {error_msg}", file=sys.stderr)


# pylint: disable=too-many-return-statements, too-many-branches, too-many-statements
def append_shared(executable_name: str, argv: list[str]) -> int:
    """
    Single function called by all three tools to append to, add to, or
    overwrite a file.
    """

    # pylint: disable=global-statement
    global _executable_name
    _executable_name = executable_name
    if executable_name not in ("append", "append-once", "overwrite"):
        _print_error("Unrecognized executable!")
        return 1

    if len(argv) != 2:
        _print_usage()
        return 1

    file_path: Path = Path(argv[0])
    orig_file_path: Path = file_path
    line_to_append: str = argv[1]
    file_contents: str = ""

    if not executable_name == "overwrite":
        try:
            file_path = file_path.resolve()
        except Exception:
            _print_error(
                f"Error while resolving path '{str(orig_file_path)}'!"
            )
            return 1

    if not os.access(file_path.parent, os.W_OK):
        _print_error(f"Folder '{str(file_path.parent)}' is not writable!")
        return 1

    file_exists: bool = file_path.exists()
    file_is_file: bool = file_path.is_file()

    if file_exists:
        if not file_is_file:
            _print_error(f"'{str(orig_file_path)}' is not a file!")
            return 1
        if executable_name != "overwrite":
            if not os.access(file_path, os.R_OK):
                _print_error(f"File '{str(orig_file_path)}' not readable!")
                return 1
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    file_contents = f.read()
                except Exception:
                    _print_error(
                        f"Error while reading file '{str(orig_file_path)}'!"
                    )
                    return 1
                if len(file_contents) != 0 and not file_contents.endswith(
                    "\n"
                ):
                    ## Fix a missing terminating newline. Some text editors
                    ## will fail to write these properly and it will break our
                    ## line appending if we don't correct it first.
                    file_contents += "\n"
    else:
        _print_info(f"File does not exist yet: '{str(orig_file_path)}'")

    if not line_to_append.endswith("\n"):
        line_to_append += "\n"

    if executable_name == "append-once":
        ## Look for a whole line match, not just a substring match. The extra
        ## newline at the beginning of line_to_append ensures that
        ## line_to_append occurs on a line by itself, the extra newline at the
        ## beginning of file_contents allows line_to_append to match the first
        ## line of the file.
        if "\n" + line_to_append in "\n" + file_contents:
            _print_info(f"Line already exists in: '{str(orig_file_path)}'")
            return 0

    file_contents += line_to_append

    if executable_name == "overwrite":
        _print_info(f"Overwriting file: '{str(orig_file_path)}'")
    else:
        _print_info(f"Appending data to: '{str(orig_file_path)}'")

    temp_file = None
    try:
        # pylint: disable=consider-using-with
        temp_file = NamedTemporaryFile(mode="w", delete=False)
        temp_file.write(file_contents)
        temp_file.flush()
        temp_file.close()
        if file_path.exists():
            shutil.copymode(file_path, temp_file.name)
        else:
            current_umask = os.umask(0)
            os.umask(current_umask)
            new_mode = 0o666 & (current_umask ^ 0o777)
            os.chmod(temp_file.name, new_mode)
        shutil.move(temp_file.name, file_path)
    except Exception:
        try:
            if temp_file is not None:
                Path(temp_file.name).unlink()
        except Exception:
            _print_error(
                f"Error while writing file '{str(orig_file_path)}', and "
                + "could not delete temp file!"
            )
            return 1
        _print_error(
            f"Error while writing file '{str(orig_file_path)}', is "
            + f"'{str(file_path.parent)}' marked as sticky?"
        )
        return 1

    return 0
