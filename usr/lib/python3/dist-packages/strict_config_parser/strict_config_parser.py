#!/usr/bin/python3 -su

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

# pylint: disable=broad-exception-caught

"""
A configuration parsing library based on tomllib that strictly validates
configuration files against a schema.
"""

from pathlib import Path
from typing import Any
import tomllib
import schema  # type: ignore


def merge_config_dict(
    master_dict: dict[str, Any], sub_dict: dict[str, Any]
) -> None:
    """
    Merges two configuration directories together.
    """

    for sub_dict_key, sub_dict_val in sub_dict.items():
        if sub_dict_key not in master_dict:
            ## Merge in new objects wholesale
            master_dict[sub_dict_key] = sub_dict_val
        else:
            master_obj_type = type(master_dict[sub_dict_key])
            sub_obj_type = type(sub_dict[sub_dict_key])
            if master_obj_type != sub_obj_type:
                raise ValueError(
                    f"Conflict on '{sub_dict_key}'; expected type "
                    f"'{str(master_obj_type)}', got type "
                    f"'{str(sub_obj_type)}'"
                )
            if isinstance(sub_dict_val, list):
                ## Add all items from lists
                master_dict[sub_dict_key].extend(sub_dict[sub_dict_key])
            elif isinstance(sub_dict_val, dict):
                ## Merge together nested dicts
                merge_config_dict(
                    master_dict[sub_dict_key], sub_dict[sub_dict_key]
                )
            else:
                ## Overwrite everything else
                master_dict[sub_dict_key] = sub_dict[sub_dict_key]


def parse_config_files(
    conf_item_list: list[str],
    conf_schema: schema.Schema,
    defaults_dict: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Parses a prioritized list of configuration files and directories, and
    returns a single configuration object containing the config from all files
    and directories overlaid. Validates the configuration against a schema.

    Each item in conf_item_list may be a path to either a file or a directory.
    If it points to a file, that file will be inserted into the list of files
    to parse. If it points to a directory, all .conf files in that directory
    will be sorted and inserted into the list of files to parse.
    """

    master_config_dict: dict[str, Any] = {}

    config_file_list: list[Path] = []

    if defaults_dict is not None:
        merge_config_dict(master_config_dict, defaults_dict)

    for conf_item in conf_item_list:
        conf_path: Path = Path(conf_item)
        if conf_path.is_file():
            config_file_list.append(conf_path)
            continue
        if conf_path.is_dir():
            config_file_sub_list: list[Path] = []
            for sub_conf_file in conf_path.iterdir():
                if not sub_conf_file.is_file():
                    continue
                if not sub_conf_file.name.endswith(".conf"):
                    continue
                config_file_sub_list.append(sub_conf_file)
            config_file_sub_list.sort()
            config_file_list.extend(config_file_sub_list)
        ## Intentional fall-through; if an item points to neither a file nor
        ## a directory, we ignore it entirely.

    for config_file in config_file_list:
        with open(config_file, "rb") as f:
            new_config_dict: dict[str, Any] = tomllib.load(f)
            merge_config_dict(master_config_dict, new_config_dict)

    conf_schema.validate(master_config_dict)
    return master_config_dict
