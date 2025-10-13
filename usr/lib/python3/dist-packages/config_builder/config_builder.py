#!/usr/bin/python3 -su

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

"""
config_builder.py: Builds configuration directories containing INI-style
configuration into a single configuration file.
"""

import re
from pathlib import Path


def config_file_to_config_state(
    config_file: Path,
) -> dict[str, dict[str, str]]:
    """
    Reads an INI-style configuration file and returns a dictionary
    representing the configuration options within.
    """

    config_state: dict[str, dict[str, str]] = {}
    detect_comment_regex: re.Pattern[str] = re.compile(r"\s*#")
    detect_header_regex: re.Pattern[str] = re.compile(r"\[.*]\Z")
    ## We don't use None here since an empty string is a valid header value
    ## (this is used to deal with the annoying fact that toml allows
    ## configuration values outside of sections). We could technically use
    ## None here but then we'd have to do gymnastics with the type checker to
    ## get it to understand the data structure. This is clearer and easier.
    current_header_str: str = ""

    with open(config_file, "r", encoding="utf-8") as config_data:
        for config_line in config_data:
            config_line = config_line.strip()
            if config_line == "":
                continue

            if detect_comment_regex.match(config_line):
                continue

            if detect_header_regex.match(config_line):
                if len(config_line) == 2:
                    raise ValueError("Empty header")
                current_header_str = config_line[1 : len(config_line) - 1]
                if not current_header_str in config_state:
                    config_state[current_header_str] = {}
                continue

            if current_header_str == "" and "" not in config_state:
                config_state[""] = {}

            if not "=" in config_line:
                raise ValueError("Config line missing equals sign")

            config_line_parts: list[str] = config_line.split("=", maxsplit=1)
            config_key: str = config_line_parts[0]
            config_val: str = config_line_parts[1]
            config_state[current_header_str][config_key] = config_val

    return config_state


def merge_down_config_state(
    base_config_state: dict[str, dict[str, str]],
    add_config_state: dict[str, dict[str, str]],
) -> None:
    """
    Merges one config state dictionary into another one.

    NOTE: Sections and keys that start with a tilde ('~') are REMOVED from the
    base state, not merged. This allows later config files to delete sections
    and keys from earlier files, which is required to properly configure
    greetd. If you need to actually start a config key with a tilde, use a
    double-tilde and it will be compressed down to a single tilde.
    """

    for key, value in add_config_state.items():
        if key.startswith("~") and not key.startswith("~~"):
            key = key[1:]
            if key in base_config_state:
                del base_config_state[key]
            continue

        if key.startswith("~~"):
            key = key[1:]

        if not key in base_config_state:
            base_config_state[key] = {}

        for nest_key, nest_value in value.items():
            if nest_key.startswith("~") and not nest_key.startswith("~~"):
                nest_key = nest_key[1:]
                if nest_key in base_config_state[key]:
                    del base_config_state[key][nest_key]
                continue

            if nest_key.startswith("~~"):
                nest_key = nest_key[1:]

            base_config_state[key][nest_key] = nest_value


def write_config_file(
    config_state: dict[str, dict[str, str]],
    output_file: Path,
) -> None:
    """
    Serializes a config state dictionary to a file.
    """

    with open(output_file, "w", encoding="utf-8") as output_stream:
        ## Write values that are outside of any particular section first
        if "" in config_state:
            for nest_key, nest_value in config_state[""].items():
                output_stream.write(f"{nest_key}={nest_value}\n")
            output_stream.write("\n")

        ## Now write all the sections
        for key, value in config_state.items():
            if key == "":
                continue
            output_stream.write(f"[{key}]\n")
            for nest_key, nest_value in value.items():
                output_stream.write(f"{nest_key}={nest_value}\n")
            output_stream.write("\n")


def build_config_file(config_dir: Path, output_file: Path) -> None:
    """
    Builds a config dir into a config file.
    """

    config_state: dict[str, dict[str, str]] = {}
    config_file_list: list[Path] = []

    for config_file in config_dir.iterdir():
        if not config_file.is_file():
            continue
        config_file_list.append(config_file)
    config_file_list.sort()

    for config_file in config_file_list:
        merge_down_config_state(
            config_state, config_file_to_config_state(config_file)
        )

    write_config_file(config_state, output_file)
