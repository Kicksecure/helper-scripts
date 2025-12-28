#!/usr/bin/python3 -su

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

# pylint: disable=missing-module-docstring,unknown-option-value

import unittest
from typing import Any
import tempfile
from pathlib import Path
import tomllib
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
            except (ValueError, schema.SchemaError, tomllib.TOMLDecodeError):
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

        ## Simple one-line valid config
        self._run_test(
            raw_config_list=[("file.conf", 'mystr = "str"\n')],
            conf_schema=mystr_schema,
            expect_error=False,
            expected_config={"mystr": "str"},
        )

        ## Simple one-line config, str/int type mismatch
        self._run_test(
            raw_config_list=[("file.conf", "mystr = 1\n")],
            conf_schema=mystr_schema,
            expect_error=True,
            expected_config={},
        )

        ## Simple one-line config, unrecognized key
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

        ## Simple two-line valid config
        self._run_test(
            raw_config_list=[("file.conf", 'mystr = "str"\nmyint = 1\n')],
            conf_schema=twokey_schema,
            expect_error=False,
            expected_config={"mystr": "str", "myint": 1},
        )

        ## Simple two-line valid config, reversed keys
        self._run_test(
            raw_config_list=[("file.conf", 'myint = 1\nmystr = "str"\n')],
            conf_schema=twokey_schema,
            expect_error=False,
            expected_config={"mystr": "str", "myint": 1},
        )

        ## Simple two-line config, missing mandatory 'mystr' key
        self._run_test(
            raw_config_list=[("file.conf", "myint = 1\n")],
            conf_schema=twokey_schema,
            expect_error=True,
            expected_config={},
        )

        ## Simple two-line config, missing mandatory 'myint' key
        self._run_test(
            raw_config_list=[("file.conf", 'mystr = "str"\n')],
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

        ## Valid config file
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

        ## Missing "do_thing" key under "settings"
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

        ## Missing "speed" key under "settings"
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

        ## Missing entire "settings" table
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

        ## Missing everything but the "settings" table
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

        ## Valid config, all data present
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

        ## Valid config, missing "do_thing" key under "settings"
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

        ## Valid config, missing "speed" key under "settings"
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

        ## Valid config, missing entire "settings" table
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

        ## Valid config, missing everything but the "settings" table
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

        ## Valid config, "settings" key split into a secondary file
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

        ## Valid config, "do_thing" key under "settings" overridden by
        ## secondary file
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

        ## Invalid config, unrecognized table "settings_oops" in secondary
        ## config file
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

        ## Invalid config, unrecognized key "nonexistent" in secondary
        ## config file
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

        ## Invalid config, "settings" table redefined as a string in secondary
        ## config file
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
settings = "wrong type entirely"
""",
                ),
            ],
            conf_schema=all_optional_complex_schema,
            expect_error=True,
            expected_config={},
        )

        # ---

        complex_list_schema: schema.Schema = schema.Schema(
            {
                schema.Optional("mystr"): str,
                schema.Optional("mylist"): [str],
            }
        )

        ## Valid config, extending "mylist" in secondary config file
        self._run_test(
            raw_config_list=[
                (
                    "confdir/50_main.conf",
                    """\
mystr="abc"
mylist=["def", "ghi"]
""",
                ),
                (
                    "confdir/60_secondary.conf",
                    """\
mylist=["jkl", "mno"]
""",
                ),
            ],
            conf_schema=complex_list_schema,
            expect_error=False,
            expected_config={
                "mystr": "abc",
                "mylist": ["def", "ghi", "jkl", "mno"],
            },
        )

        ## Invalid config, type mismatch within list in secondary config file
        self._run_test(
            raw_config_list=[
                (
                    "confdir/50_main.conf",
                    """\
mystr="abc"
mylist=["def", "ghi"]
""",
                ),
                (
                    "confdir/60_secondary.conf",
                    """\
mylist=["jkl", 1]
""",
                ),
            ],
            conf_schema=complex_list_schema,
            expect_error=True,
            expected_config={},
        )

        ## Invalid config, list redefined as string in secondary config file
        self._run_test(
            raw_config_list=[
                (
                    "confdir/50_main.conf",
                    """\
mystr="abc"
mylist=["def", "ghi"]
""",
                ),
                (
                    "confdir/60_secondary.conf",
                    """\
mylist="not a list"
""",
                ),
            ],
            conf_schema=complex_list_schema,
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

        ## Valid config, config override test 1 (single file in secondary
        ## config dir)
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

        ## Valid config, config override test 2 (multiple files in each
        ## config dir)
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

        ## Invalid config, unrecognized key "do_thing_mess"
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

        ## Valid config, ignored configuration files in secondary and tertiary
        ## config dirs
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
                (
                    "confdir2/README.md",
                    """\
# This isn't a config file at all.

It's a Markdown file. It **should** be ignored.
""",
                ),
                (
                    "confdir3/whatever.cofn",
                    """\
mode = "this should be ignored"
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

        ## Valid config, default values populate "level" key and are otherwise
        ## overridden
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

        ## Invalid config, "mode" key incorrectly defined as boolean
        ## by defaults
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
            expect_error=True,
            expected_config={},
            default_config={
                "mode": True,
                "level": 3,
                "settings": {"do_thing": False},
            },
        )

    def test_malformed_toml(self) -> None:
        """
        Tests that malformed TOML is properly rejected.
        """

        mystr_schema: schema.Schema = schema.Schema({"mystr": str})

        ## Invalid config, missing quotes around "mystr" value
        self._run_test(
            raw_config_list=[("file.conf", "mystr = a\n")],
            conf_schema=mystr_schema,
            expect_error=True,
            expected_config={},
        )

        ## Invalid config, secondary config file is missing a quote around
        ## "mystr" value
        self._run_test(
            raw_config_list=[
                ("file.conf", 'mystr = "works"\n'),
                (
                    "file2.conf",
                    'mystr = "nope\n',
                ),
            ],
            conf_schema=mystr_schema,
            expect_error=True,
            expected_config={},
        )
