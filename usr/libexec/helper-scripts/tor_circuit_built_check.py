#!/usr/bin/python3 -Bsu

## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## AI-Assisted

## Actively build one fresh circuit (EXTENDCIRCUIT 0, Tor's own path
## selection - no named destination) and wait for it to reach BUILT. Unlike
## the sticky status/circuit-established flag, BUILT cannot be a stale false
## positive (tor#28027, tor#21422).
##
## Exit codes (mirroring tor-circuit-established-check):
##   0   - a circuit reached BUILT within the timeout
##   1   - no circuit reached BUILT within the timeout
##   255 - could not connect to the Tor control port
##
## Usage: tor_circuit_built_check.py [timeout_seconds]  (default 30)

import sys
import stem
from stem.connection import connect

try:
    timeout = float(sys.argv[1])
except (IndexError, ValueError):
    timeout = 30.0

controller = connect()

if not controller:
    sys.exit(255)

try:
    circuit_id = controller.new_circuit(
        purpose="general", await_build=True, timeout=timeout
    )
## stem.Timeout subclasses stem.ControllerError, so catch it first.
except stem.Timeout:
    controller.close()
    print("no new circuit reached BUILT within {}s".format(timeout))
    sys.exit(1)
except stem.ControllerError as build_error:
    controller.close()
    print("circuit build failed: {}".format(build_error))
    sys.exit(1)

controller.close()

print("CIRC {} BUILT".format(circuit_id))
sys.exit(0)
