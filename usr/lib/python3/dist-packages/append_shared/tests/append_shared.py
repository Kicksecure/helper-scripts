#!/usr/bin/python3 -Bsu

## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

"""
Tests for the append_shared tools.
"""

import os
import stat
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from append_shared.append_shared import append_shared


# pylint: disable=too-many-public-methods
class TestAppendShared(TestCase):
    """
    Tests for append_shared.py.
    """

    work_dir: str

    @classmethod
    def setUpClass(cls) -> None:
        """
        Create a temporary directory to work in.
        """

        with TemporaryDirectory(delete=False) as td:
            cls.work_dir = td

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Clean up the temporary directory.
        """

        shutil.rmtree(cls.work_dir)
        cls.work_dir = ""

    def test_reject_unrecognized_executable(self) -> None:
        """
        Tests if append-once properly rejects an unrecognized executable name.
        """

        self.assertEqual(append_shared("nope", ["abc", "def"]), 1)

    def test_append_create(self) -> None:
        """
        Tests if 'append' can create a file.
        """

        target_file: str = self.work_dir + "/append_create"
        self.assertEqual(
            append_shared("append", [target_file, "append_created"]), 0
        )
        self.assertEqual(
            Path(target_file).read_text(encoding="utf-8"), "append_created\n"
        )
        os.unlink(target_file)

    def test_append_once_create(self) -> None:
        """
        Tests if 'append-once' can create a file.
        """

        target_file: str = self.work_dir + "/append_once_create"
        self.assertEqual(
            append_shared("append-once", [target_file, "append_once_created"]),
            0,
        )
        self.assertEqual(
            Path(target_file).read_text(encoding="utf-8"),
            "append_once_created\n",
        )
        os.unlink(target_file)

    def test_overwrite_create(self) -> None:
        """
        Tests if 'overwrite' can create a file.
        """

        target_file: str = self.work_dir + "/overwrite_create"
        self.assertEqual(
            append_shared("overwrite", [target_file, "overwrite_created"]), 0
        )
        self.assertEqual(
            Path(target_file).read_text(encoding="utf-8"),
            "overwrite_created\n",
        )
        os.unlink(target_file)

    def test_append_add(self) -> None:
        """
        Tests if 'append' can add a line to a file.
        """

        target_file: str = self.work_dir + "/append_add"
        target_file_path: Path = Path(target_file)
        target_file_path.write_text("line 1\n", encoding="utf-8")
        self.assertEqual(append_shared("append", [target_file, "line 2"]), 0)
        self.assertEqual(
            target_file_path.read_text(encoding="utf-8"), "line 1\nline 2\n"
        )
        os.unlink(target_file)

    def test_append_once_add(self) -> None:
        """
        Tests if 'append-once' can add a line to a file.
        """

        target_file: str = self.work_dir + "/append_once_add"
        target_file_path: Path = Path(target_file)
        target_file_path.write_text("line 1\n", encoding="utf-8")
        self.assertEqual(
            append_shared("append-once", [target_file, "line 2"]), 0
        )
        self.assertEqual(
            target_file_path.read_text(encoding="utf-8"), "line 1\nline 2\n"
        )
        os.unlink(target_file)

    def test_overwrite_clobber_file(self) -> None:
        """
        Tests if 'overwrite' can clobber a file's existing contents.
        """

        target_file: str = self.work_dir + "/overwrite_clobber"
        target_file_path: Path = Path(target_file)
        target_file_path.write_text("line 1\n", encoding="utf-8")
        self.assertEqual(
            append_shared("overwrite", [target_file, "line 2"]), 0
        )
        self.assertEqual(
            target_file_path.read_text(encoding="utf-8"), "line 2\n"
        )
        os.unlink(target_file)

    def test_append_add_dup(self) -> None:
        """
        Tests if 'append' can add a duplicate line to a file.
        """

        target_file: str = self.work_dir + "/append_dup"
        target_file_path: Path = Path(target_file)
        target_file_path.write_text(
            "The first line\nThe second line\nThe third line\n",
            encoding="utf-8",
        )
        self.assertEqual(
            append_shared("append", [target_file, "The second line"]), 0
        )
        self.assertEqual(
            target_file_path.read_text(encoding="utf-8"),
            "The first line\nThe second line\n"
            + "The third line\nThe second line\n",
        )
        os.unlink(target_file)

    def test_append_once_reject_dup(self) -> None:
        """
        Tests if 'append-once' properly rejects an attempt to add a duplicate
        line.
        """

        target_file: str = self.work_dir + "/append_once_dup"
        target_file_path: Path = Path(target_file)
        target_file_path.write_text(
            "The first line\nThe second line\nThe third line\n",
            encoding="utf-8",
        )
        self.assertEqual(
            append_shared("append-once", [target_file, "The first line"]), 0
        )
        self.assertEqual(
            target_file_path.read_text(encoding="utf-8"),
            "The first line\nThe second line\nThe third line\n",
        )
        self.assertEqual(
            append_shared("append-once", [target_file, "The second line"]), 0
        )
        self.assertEqual(
            target_file_path.read_text(encoding="utf-8"),
            "The first line\nThe second line\nThe third line\n",
        )
        self.assertEqual(
            append_shared("append-once", [target_file, "The third line"]), 0
        )
        self.assertEqual(
            target_file_path.read_text(encoding="utf-8"),
            "The first line\nThe second line\nThe third line\n",
        )
        os.unlink(target_file)

    def test_append_once_add_partial_dup(self) -> None:
        """
        Tests if 'append-once' allows appending a new line that is unique, but
        consists of a substring of an existing line.
        """

        target_file: str = self.work_dir + "/append_once_partial_dup"
        target_file_path: Path = Path(target_file)
        target_file_path.write_text(
            "The first line\nThe second line\nThe third line\n",
            encoding="utf-8",
        )
        self.assertEqual(
            append_shared("append-once", [target_file, "The first"]), 0
        )
        self.assertEqual(
            target_file_path.read_text(encoding="utf-8"),
            "The first line\nThe second line\nThe third line\nThe first\n",
        )
        self.assertEqual(
            append_shared("append-once", [target_file, "second"]), 0
        )
        self.assertEqual(
            target_file_path.read_text(encoding="utf-8"),
            "The first line\nThe second line\nThe third line\n"
            + "The first\nsecond\n",
        )
        self.assertEqual(
            append_shared("append-once", [target_file, "third line"]), 0
        )
        self.assertEqual(
            target_file_path.read_text(encoding="utf-8"),
            "The first line\nThe second line\nThe third line\n"
            + "The first\nsecond\nthird line\n",
        )
        os.unlink(target_file)

    def test_append_repair_newline(self) -> None:
        """
        Tests if 'append' repairs a file with a missing terminating newline
        before appending a line to it.
        """

        target_file: str = self.work_dir + "/append_repair_newline"
        target_file_path: Path = Path(target_file)
        target_file_path.write_text("line 1\nline 2", encoding="utf-8")
        self.assertEqual(append_shared("append", [target_file, "line 3"]), 0)
        self.assertEqual(
            target_file_path.read_text(encoding="utf-8"),
            "line 1\nline 2\nline 3\n",
        )
        os.unlink(target_file)

    def test_append_once_repair_newline(self) -> None:
        """
        Tests if 'append' repairs a file with a missing terminating newline
        before appending a line to it.
        """

        target_file: str = self.work_dir + "/append_once_repair_newline"
        target_file_path: Path = Path(target_file)
        target_file_path.write_text("line 1\nline 2", encoding="utf-8")
        self.assertEqual(
            append_shared("append-once", [target_file, "line 3"]), 0
        )
        self.assertEqual(
            target_file_path.read_text(encoding="utf-8"),
            "line 1\nline 2\nline 3\n",
        )
        os.unlink(target_file)

    def test_append_empty_string(self) -> None:
        """
        Tests if using 'append-once' to append an empty string results in a
        single empty line being appended to the file.
        """

        target_file: str = self.work_dir + "/append_empty_string"
        target_file_path: Path = Path(target_file)
        target_file_path.write_text("line 1\n", encoding="utf-8")
        self.assertEqual(append_shared("append", [target_file, ""]), 0)
        self.assertEqual(
            target_file_path.read_text(encoding="utf-8"), "line 1\n\n"
        )
        os.unlink(target_file)

    def test_append_once_empty_string(self) -> None:
        """
        Tests if using 'append-once' to append an empty string results in a
        single empty line being appended to the file.
        """

        target_file: str = self.work_dir + "/append_once_empty_string"
        target_file_path: Path = Path(target_file)
        target_file_path.write_text("line 1\n", encoding="utf-8")
        self.assertEqual(append_shared("append-once", [target_file, ""]), 0)
        self.assertEqual(
            target_file_path.read_text(encoding="utf-8"), "line 1\n\n"
        )
        os.unlink(target_file)

    def test_append_empty_string_repair_newline(self) -> None:
        """
        Tests if using 'append' to append an empty string to a file with a
        missing terminating newline repairs the file and appends an additional
        blank line.
        """

        target_file: str = (
            self.work_dir + "/append_empty_string_repair_newline"
        )
        target_file_path: Path = Path(target_file)
        target_file_path.write_text("line 1\nline 2", encoding="utf-8")
        self.assertEqual(append_shared("append", [target_file, ""]), 0)
        self.assertEqual(
            target_file_path.read_text(encoding="utf-8"), "line 1\nline 2\n\n"
        )
        os.unlink(target_file)

    def test_append_once_empty_string_repair_newline(self) -> None:
        """
        Tests if using 'append-once' to append an empty string to a file with
        a missing terminating newline repairs the file and appends an
        additional blank line.
        """

        target_file: str = (
            self.work_dir + "/append_once_empty_string_repair_newline"
        )
        target_file_path: Path = Path(target_file)
        target_file_path.write_text("line 1\nline 2", encoding="utf-8")
        self.assertEqual(append_shared("append-once", [target_file, ""]), 0)
        self.assertEqual(
            target_file_path.read_text(encoding="utf-8"), "line 1\nline 2\n\n"
        )
        os.unlink(target_file)

    def test_append_once_reject_dup_empty_string(self) -> None:
        """
        Tests if 'append-once' refuses to append a blank line to a file that
        already has an empty line somewhere in it.
        """

        target_file: str = (
            self.work_dir + "/append_once_reject_dup_empty_string"
        )
        target_file_path: Path = Path(target_file)
        target_file_path.write_text("\nline 1\nline 2\n", encoding="utf-8")
        self.assertEqual(append_shared("append-once", [target_file, ""]), 0)
        self.assertEqual(
            target_file_path.read_text(encoding="utf-8"), "\nline 1\nline 2\n"
        )
        target_file_path.write_text("line 1\n\nline 2\n", encoding="utf-8")
        self.assertEqual(append_shared("append-once", [target_file, ""]), 0)
        self.assertEqual(
            target_file_path.read_text(encoding="utf-8"), "line 1\n\nline 2\n"
        )
        target_file_path.write_text("line 1\nline 2\n\n", encoding="utf-8")
        self.assertEqual(append_shared("append-once", [target_file, ""]), 0)
        self.assertEqual(
            target_file_path.read_text(encoding="utf-8"), "line 1\nline 2\n\n"
        )
        os.unlink(target_file)

    def test_append_reject_unwritable_parent_dir(self) -> None:
        """
        Tests if 'append' refuses to try to write a file in a directory it
        lacks write permissions to.
        """

        target_file: str = (
            self.work_dir + "/append_reject_unwritable_parent_dir"
        )
        target_file_path: Path = Path(target_file)
        target_file_path.write_text("line 1\n", encoding="utf-8")
        os.chmod(self.work_dir, stat.S_IRUSR | stat.S_IXUSR)
        self.assertEqual(append_shared("append", [target_file, "line 2"]), 1)
        self.assertEqual(
            target_file_path.read_text(encoding="utf-8"), "line 1\n"
        )
        os.chmod(self.work_dir, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
        os.unlink(target_file)

    def test_append_reject_dir(self) -> None:
        """
        Tests if 'append' refuses to attempt to append to a directory.
        """

        target_dir: str = self.work_dir + "/append_reject_dir"
        os.mkdir(target_dir)
        self.assertEqual(append_shared("append", [target_dir, "nope"]), 1)
        os.rmdir(target_dir)
