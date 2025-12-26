#!/usr/bin/python3 -su

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

# pylint: disable=missing-module-docstring

import unittest
from typing import Any
import tempfile
from pathlib import Path
import schema  # type: ignore
from strict_config_parser.strict_config_parser import parse_config_files


class TestStrictConfigParser(unittest.TestCase):
    """
    Tests for strict_config_parser.py.
    """

    maxDiff = None

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def _run_test(
        self,
        raw_config_list: list[tuple[str, str]],
        conf_schema: schema.Schema,
        expect_error: bool,
        expected_config: dict[str, Any],
        default_config: dict[str, Any] | None = None,
    ) -> None:
        """
        Given a list of configuration files and contents, ensures that:

        - If 'expect_error' is False, the resulting config either parses into
          the expected dictionary and passes a schema.
        - If 'expect_error' is True, the resulting config errors out due to a
          parse or schema issue.
        """

        with tempfile.TemporaryDirectory() as temp_dir:
            for raw_config_key, raw_config_val in raw_config_list:
                target_dir_path: Path = (
                    Path(temp_dir) / Path(raw_config_key).parent
                )
                target_dir_path.mkdir(parents=True, exist_ok=True)
                target_file_path: Path = (
                    target_dir_path / Path(raw_config_key).name
                )
                target_file_path.write_text(raw_config_val)
            conf_item_list: list[str] = [
                str(x) for x in Path(temp_dir).iterdir()
            ]
            conf_item_list.sort()
            try:
                parsed_config: dict[str, Any] = parse_config_files(
                    conf_item_list=conf_item_list,
                    conf_schema=conf_schema,
                    defaults_dict=default_config,
                )
                self.assertFalse(expect_error)
                self.assertEqual(expected_config, parsed_config)
            except (ValueError, schema.SchemaError):
                self.assertTrue(expect_error)

    def test_empty(self) -> None:
        """
        Tests parsing "nothing".
        """

        self._run_test([], schema.Schema({}), False, {})

    def test_single(self) -> None:
        """
        Tests parsing a single config file. This mostly just exercises the
        tomllib and schema libraries.
        """

        mystr_schema: schema.Schema = schema.Schema({"mystr": str})
        self._run_test(
            raw_config_list=[("file.conf", 'mystr = "str"\n')],
            conf_schema=mystr_schema,
            expect_error=False,
            expected_config={"mystr": "str"},
        )
        self._run_test(
            raw_config_list=[("file.conf", "mystr = 1\n")],
            conf_schema=mystr_schema,
            expect_error=True,
            expected_config={},
        )
        self._run_test(
            raw_config_list=[("file.conf", 'wha = "nope"\n')],
            conf_schema=mystr_schema,
            expect_error=True,
            expected_config={},
        )

        # ---

        twokey_schema: schema.Schema = schema.Schema(
            {"mystr": str, "myint": int}
        )
        self._run_test(
            raw_config_list=[("file.conf", 'mystr = "str"\nmyint = 1\n')],
            conf_schema=twokey_schema,
            expect_error=False,
            expected_config={"mystr": "str", "myint": 1},
        )
        self._run_test(
            raw_config_list=[("file.conf", 'myint = 1\nmystr = "str"\n')],
            conf_schema=twokey_schema,
            expect_error=False,
            expected_config={"mystr": "str", "myint": 1},
        )
        self._run_test(
            raw_config_list=[("file.conf", "myint = 1\n")],
            conf_schema=twokey_schema,
            expect_error=True,
            expected_config={},
        )
        self._run_test(
            raw_config_list=[("file.conf", 'mystr = "str"\n')],
            conf_schema=twokey_schema,
            expect_error=True,
            expected_config={},
        )
        self._run_test(
            raw_config_list=[("file.conf", "mystr = str\n")],
            conf_schema=twokey_schema,
            expect_error=True,
            expected_config={},
        )

        # ---

        complex_schema: schema.Schema = schema.Schema(
            {
                "mode": str,
                "level": int,
                "settings": {"do_thing": bool, "speed": int},
            }
        )
        self._run_test(
            raw_config_list=[
                (
                    "file.conf",
                    """\
# This is a comment.
mode = "default"
level = 5

[settings]
do_thing = true
speed = 123
""",
                )
            ],
            conf_schema=complex_schema,
            expect_error=False,
            expected_config={
                "mode": "default",
                "level": 5,
                "settings": {"do_thing": True, "speed": 123},
            },
        )
        self._run_test(
            raw_config_list=[
                (
                    "file.conf",
                    """\
# This is a comment.
mode = "default"
level = 5

[settings]
speed = 123
""",
                )
            ],
            conf_schema=complex_schema,
            expect_error=True,
            expected_config={},
        )
        self._run_test(
            raw_config_list=[
                (
                    "file.conf",
                    """\
# This is a comment.
mode = "default"
level = 5

[settings]
do_thing = true
""",
                )
            ],
            conf_schema=complex_schema,
            expect_error=True,
            expected_config={},
        )
        self._run_test(
            raw_config_list=[
                (
                    "file.conf",
                    """\
# This is a comment.
mode = "default"
level = 5
""",
                )
            ],
            conf_schema=complex_schema,
            expect_error=True,
            expected_config={},
        )
        self._run_test(
            raw_config_list=[
                (
                    "file.conf",
                    """\
[settings]
do_thing = true
speed = 123
""",
                )
            ],
            conf_schema=complex_schema,
            expect_error=True,
            expected_config={},
        )

        # ---

        all_optional_complex_schema: schema.Schema = schema.Schema(
            {
                schema.Optional("mode"): str,
                schema.Optional("level"): int,
                schema.Optional("settings"): {
                    schema.Optional("do_thing"): bool,
                    schema.Optional("speed"): int,
                },
            }
        )
        self._run_test(
            raw_config_list=[
                (
                    "file.conf",
                    """\
# This is a comment.
mode = "default"
level = 5

[settings]
do_thing = true
speed = 123
""",
                )
            ],
            conf_schema=all_optional_complex_schema,
            expect_error=False,
            expected_config={
                "mode": "default",
                "level": 5,
                "settings": {
                    "do_thing": True,
                    "speed": 123,
                },
            },
        )
        self._run_test(
            raw_config_list=[
                (
                    "file.conf",
                    """\
# This is a comment.
mode = "default"
level = 5

[settings]
speed = 123
""",
                )
            ],
            conf_schema=all_optional_complex_schema,
            expect_error=False,
            expected_config={
                "mode": "default",
                "level": 5,
                "settings": {
                    "speed": 123,
                },
            },
        )
        self._run_test(
            raw_config_list=[
                (
                    "file.conf",
                    """\
# This is a comment.
mode = "default"
level = 5

[settings]
do_thing = true
""",
                )
            ],
            conf_schema=all_optional_complex_schema,
            expect_error=False,
            expected_config={
                "mode": "default",
                "level": 5,
                "settings": {
                    "do_thing": True,
                },
            },
        )
        self._run_test(
            raw_config_list=[
                (
                    "file.conf",
                    """\
# This is a comment.
mode = "default"
level = 5
""",
                )
            ],
            conf_schema=all_optional_complex_schema,
            expect_error=False,
            expected_config={
                "mode": "default",
                "level": 5,
            },
        )
        self._run_test(
            raw_config_list=[
                (
                    "file.conf",
                    """\
[settings]
do_thing = true
speed = 123
""",
                )
            ],
            conf_schema=all_optional_complex_schema,
            expect_error=False,
            expected_config={
                "settings": {
                    "do_thing": True,
                    "speed": 123,
                },
            },
        )

    def test_dir(self) -> None:
        """
        Tests parsing a directory of config files.
        """

        all_optional_complex_schema: schema.Schema = schema.Schema(
            {
                schema.Optional("mode"): str,
                schema.Optional("level"): int,
                schema.Optional("settings"): {
                    schema.Optional("do_thing"): bool,
                    schema.Optional("speed"): int,
                },
            }
        )
        self._run_test(
            raw_config_list=[
                (
                    "confdir/50_main.conf",
                    """\
mode = "default"
level = 5
""",
                ),
                (
                    "confdir/60_secondary.conf",
                    """\
[settings]
do_thing = true
speed = 123
""",
                ),
            ],
            conf_schema=all_optional_complex_schema,
            expect_error=False,
            expected_config={
                "mode": "default",
                "level": 5,
                "settings": {
                    "do_thing": True,
                    "speed": 123,
                },
            },
        )
        self._run_test(
            raw_config_list=[
                (
                    "confdir/50_main.conf",
                    """\
mode = "default"
level = 5

[settings]
do_thing = true
speed = 123
""",
                ),
                (
                    "confdir/60_secondary.conf",
                    """\
[settings]
do_thing = false
""",
                ),
            ],
            conf_schema=all_optional_complex_schema,
            expect_error=False,
            expected_config={
                "mode": "default",
                "level": 5,
                "settings": {
                    "do_thing": False,
                    "speed": 123,
                },
            },
        )
        self._run_test(
            raw_config_list=[
                (
                    "confdir/50_main.conf",
                    """\
mode = "default"
level = 5

[settings]
do_thing = true
speed = 123
""",
                ),
                (
                    "confdir/60_secondary.conf",
                    """\
[settings_oops]
do_thing = false
""",
                ),
            ],
            conf_schema=all_optional_complex_schema,
            expect_error=True,
            expected_config={},
        )
        self._run_test(
            raw_config_list=[
                (
                    "confdir/50_main.conf",
                    """\
mode = "default"
level = 5

[settings]
do_thing = true
speed = 123
""",
                ),
                (
                    "confdir/60_secondary.conf",
                    """\
nonexistent = "what's this doing here"

[settings]
do_thing = false
""",
                ),
            ],
            conf_schema=all_optional_complex_schema,
            expect_error=True,
            expected_config={},
        )

    def test_multi_dirs(self) -> None:
        """
        Tests parsing multiple directories with config files.
        """

        all_optional_complex_schema: schema.Schema = schema.Schema(
            {
                schema.Optional("mode"): str,
                schema.Optional("level"): int,
                schema.Optional("settings"): {
                    schema.Optional("do_thing"): bool,
                    schema.Optional("speed"): int,
                },
            }
        )
        self._run_test(
            raw_config_list=[
                (
                    "confdir1/50_main.conf",
                    """\
mode = "default"
level = 5

[settings]
do_thing = true
speed = 123
""",
                ),
                (
                    "confdir1/60_secondary.conf",
                    """\
mode = "fast"

[settings]
speed = 456
""",
                ),
                (
                    "confdir2/10_user.conf",
                    """\
mode = "slow"
level = 1
""",
                ),
            ],
            conf_schema=all_optional_complex_schema,
            expect_error=False,
            expected_config={
                "mode": "slow",
                "level": 1,
                "settings": {"do_thing": True, "speed": 456},
            },
        )
        self._run_test(
            raw_config_list=[
                (
                    "confdir1/50_main.conf",
                    """\
mode = "default"
level = 5

[settings]
do_thing = true
speed = 123
""",
                ),
                (
                    "confdir1/60_secondary.conf",
                    """\
mode = "fast"

[settings]
speed = 456
""",
                ),
                (
                    "confdir2/10_user.conf",
                    """\
mode = "slow"
level = 1
""",
                ),
                (
                    "confdir2/10_disable.conf",
                    """\
[settings]
do_thing = false
""",
                ),
            ],
            conf_schema=all_optional_complex_schema,
            expect_error=False,
            expected_config={
                "mode": "slow",
                "level": 1,
                "settings": {"do_thing": False, "speed": 456},
            },
        )
        self._run_test(
            raw_config_list=[
                (
                    "confdir1/50_main.conf",
                    """\
mode = "default"
level = 5

[settings]
do_thing = true
speed = 123
""",
                ),
                (
                    "confdir1/60_secondary.conf",
                    """\
mode = "fast"

[settings]
speed = 456
""",
                ),
                (
                    "confdir2/10_user.conf",
                    """\
mode = "slow"
level = 1
""",
                ),
                (
                    "confdir2/10_disable.conf",
                    """\
[settings]
do_thing_mess = false
""",
                ),
            ],
            conf_schema=all_optional_complex_schema,
            expect_error=True,
            expected_config={},
        )

    def test_default_dict(self) -> None:
        """
        Tests merging in a dictionary of default configuration options.
        """

        all_optional_complex_schema: schema.Schema = schema.Schema(
            {
                schema.Optional("mode"): str,
                schema.Optional("level"): int,
                schema.Optional("settings"): {
                    schema.Optional("do_thing"): bool,
                    schema.Optional("speed"): int,
                },
            }
        )
        self._run_test(
            raw_config_list=[
                (
                    "file.conf",
                    """\
mode = "default"

[settings]
do_thing = true
speed = 123
""",
                ),
            ],
            conf_schema=all_optional_complex_schema,
            expect_error=False,
            expected_config={
                "mode": "default",
                "level": 3,
                "settings": {
                    "do_thing": True,
                    "speed": 123,
                },
            },
            default_config={
                "mode": "slow",
                "level": 3,
                "settings": {"do_thing": False},
            },
        )
