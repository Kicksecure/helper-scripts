#!/usr/bin/python3 -u

## Copyright (C) 2012 - 2020 ENCRYPTED SUPPORT LP <adrelanos@riseup.net>
## See the file COPYING for copying conditions.

import sys
from stem.connection import connect

controller = connect()

if not controller:
    sys.exit(255)

circuit_established = controller.get_info("status/circuit-established")

## Possible answer, if established:
## 1

## Possible answer, if not established:
## 0

print(format(circuit_established))

controller.close()

sys.exit(0)
