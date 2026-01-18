#!/usr/bin/python3 -su

## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

"""
A Python wrapper around /usr/libexec/helper-scripts/get_colors.sh.
"""

import subprocess
import os
import sys


# pylint: disable=too-many-instance-attributes,too-many-statements,too-few-public-methods
class TermColors:
    """
    Sets variables that can be used for printing applicable SGR color codes
    (and related ANSI sequences) to the display.
    """

    def __init__(self) -> None:
        environ_copy: dict[str, str] = os.environ.copy()
        if sys.stderr.isatty():
            environ_copy["ASSUME_TERM_PRESENT"] = "true"
        colors_list: list[str] = subprocess.run(
            [
                "/usr/bin/bash",
                "-c",
                """\
source ../../../../../usr/libexec/helper-scripts/get_colors.sh
get_colors
printf '%s\n' "nocolor=${nocolor}
reset=${reset}
bold=${bold}
nobold=${nobold}
underline=${underline}
nounderline=${nounderline}
under=${under}
eunder=${eunder}
stout=${stout}
estout=${estout}
blink=${blink}
italic=${italic}
eitalic=${eitalic}
red=${red}
green=${green}
yellow=${yellow}
blue=${blue}
magenta=${magenta}
cyan=${cyan}
white=${white}
default=${default}
alt=${alt}
ealt=${ealt}
hide=${hide}
show=${show}
save=${save}
load=${load}
eed=${eed}
eel=${eel}
ebl=${ebl}
ewl=${ewl}
back=${back}
draw=${draw}"\
""",
            ],
            check=True,
            capture_output=True,
            encoding="utf-8",
            errors="surrogateescape",
            env=environ_copy,
        ).stdout.splitlines()
        self.nocolor: str = ""
        self.reset: str = ""
        self.bold: str = ""
        self.nobold: str = ""
        self.underline: str = ""
        self.nounderline: str = ""
        self.under: str = ""
        self.eunder: str = ""
        self.stout: str = ""
        self.estout: str = ""
        self.blink: str = ""
        self.italic: str = ""
        self.eitalic: str = ""
        self.red: str = ""
        self.green: str = ""
        self.yellow: str = ""
        self.blue: str = ""
        self.magenta: str = ""
        self.cyan: str = ""
        self.white: str = ""
        self.default: str = ""
        self.alt: str = ""
        self.ealt: str = ""
        self.hide: str = ""
        self.show: str = ""
        self.save: str = ""
        self.load: str = ""
        self.eed: str = ""
        self.eel: str = ""
        self.ebl: str = ""
        self.ewl: str = ""
        self.back: str = ""
        self.draw: str = ""
        for color_line in colors_list:
            color_parts: list[str] = color_line.split("=")
            if len(color_parts) != 2:
                continue
            color_key: str = color_parts[0]
            color_val: str = color_parts[1]
            match color_key:
                case "nocolor":
                    self.nocolor = color_val
                case "reset":
                    self.reset = color_val
                case "bold":
                    self.bold = color_val
                case "nobold":
                    self.nobold = color_val
                case "underline":
                    self.underline = color_val
                case "nounderline":
                    self.nounderline = color_val
                case "under":
                    self.under = color_val
                case "eunder":
                    self.eunder = color_val
                case "stout":
                    self.stout = color_val
                case "estout":
                    self.estout = color_val
                case "blink":
                    self.blink = color_val
                case "italic":
                    self.italic = color_val
                case "eitalic":
                    self.eitalic = color_val
                case "red":
                    self.red = color_val
                case "green":
                    self.green = color_val
                case "yellow":
                    self.yellow = color_val
                case "blue":
                    self.blue = color_val
                case "magenta":
                    self.magenta = color_val
                case "cyan":
                    self.cyan = color_val
                case "white":
                    self.white = color_val
                case "default":
                    self.default = color_val
                case "alt":
                    self.alt = color_val
                case "ealt":
                    self.ealt = color_val
                case "hide":
                    self.hide = color_val
                case "show":
                    self.show = color_val
                case "save":
                    self.save = color_val
                case "load":
                    self.load = color_val
                case "eed":
                    self.eed = color_val
                case "eel":
                    self.eel = color_val
                case "ebl":
                    self.ebl = color_val
                case "ewl":
                    self.ewl = color_val
                case "back":
                    self.back = color_val
                case "draw":
                    self.draw = color_val
