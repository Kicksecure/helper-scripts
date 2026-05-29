#!/usr/bin/python3 -Bsu

## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## AI-Assisted

## Actively build one fresh circuit and wait for it to finish
## building. Unlike the sticky status/circuit-established flag, this
## cannot be a stale false positive.
##
## Exit codes (mirroring tor-circuit-established-check):
##   0   - a circuit was built within the timeout
##   1   - no circuit was built within the timeout
##   255 - could not connect to the Tor control port
##
## Usage: tor_circuit_built_check.py [timeout_seconds]  (default 8)

import sys
import stem
from stem.connection import connect

try:
    timeout = float(sys.argv[1])
except (IndexError, ValueError):
    ## Active circuit-readiness check for onion-time-pre-script
    ## (8 seconds fits the 'leaprun' timeout in 'tor_bootstrap_check.bsh').
    timeout = 8.0

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
    print("no new circuit built within {}s".format(timeout))
    sys.exit(1)
except Exception as build_error:
    ## controller.new_circuit() can fail with more than just
    ## stem.ControllerError.
    controller.close()
    print("circuit build failed: {}".format(build_error))
    sys.exit(1)

controller.close()

print("Circuit {} built".format(circuit_id))
sys.exit(0)
