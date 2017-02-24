#!/usr/bin/python3 -u

## This file is part of Whonix.
## Copyright (C) 2012 - 2014 Patrick Schleizer <adrelanos@riseup.net>
## See the file COPYING for copying conditions.

import sys
from stem.connection import connect

controller = connect()

if not controller:
    sys.exit(255)

output = controller.get_info("consensus/valid-after")

print(format(output))

controller.close()

sys.exit(0)
