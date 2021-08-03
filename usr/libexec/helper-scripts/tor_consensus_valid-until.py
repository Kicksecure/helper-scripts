#!/usr/bin/python3 -u

## Copyright (C) 2012 - 2021 ENCRYPTED SUPPORT LP <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

import sys
from stem.connection import connect

controller = connect()

if not controller:
    sys.exit(255)

output = controller.get_info("consensus/valid-until")

print(format(output))

controller.close()

sys.exit(0)
