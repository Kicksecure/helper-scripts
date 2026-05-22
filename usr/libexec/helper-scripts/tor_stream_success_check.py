#!/usr/bin/python3 -Bsu

## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## AI-Assisted

## Check whether Tor is carrying a USABLE circuit, by observing a real
## data-carrying stream reach SUCCEEDED on the control port. A
## STREAM ... SUCCEEDED event means a CONNECTED cell was received over
## the full circuit end to end - the only signal that actually proves
## usability, as opposed to mere circuit construction.
##
## This is the honest alternative to status/circuit-established
## (tor-circuit-established-check). That value is C-Tor's sticky
## have_completed_a_circuit() flag: set once on the first MECHANICALLY
## built multi-hop circuit and reset only on a clock-jump/idle, stale
## directory info, or process teardown - never on a failed fetch. So it
## can read 1 while no circuit actually carries traffic - a false
## positive even for general-purpose (not just onion) circuits:
##   https://gitlab.torproject.org/tpo/core/tor/-/issues/28027
##   https://gitlab.torproject.org/tpo/core/tor/-/issues/21422
##
## IMPORTANT - this is a PASSIVE observer. It reports success only if a
## stream actually reaches SUCCEEDED within the timeout window; it does
## NOT generate traffic. So on an idle system, or before any
## application/onion connection has happened (for example early boot,
## before sdwdate's own time fetch), there is nothing to observe and it
## returns "not seen". Tor's own directory fetches are internal
## directory connections, not application streams, and do not emit
## STREAM events. Use it to CONFIRM usability while traffic is (or is
## being made to) flow - for example alongside sdwdate's own onion
## fetch - not as a standalone boot-time gate.
##
## Exit codes (mirroring tor-circuit-established-check):
##   0   - a stream reached SUCCEEDED within the timeout
##   1   - no stream reached SUCCEEDED within the timeout
##   255 - could not connect to the Tor control port
##
## Usage: tor_stream_success_check.py [timeout_seconds]
##   timeout_seconds: how long to wait for a SUCCEEDED stream (default 10)

import sys
import threading
from stem import StreamStatus
from stem.control import EventType
from stem.connection import connect

try:
    timeout = float(sys.argv[1])
except (IndexError, ValueError):
    timeout = 10.0

controller = connect()

if not controller:
    sys.exit(255)

seen = threading.Event()
observed = {}


def stream_event(event):
    if event.status == StreamStatus.SUCCEEDED and not seen.is_set():
        observed["target"] = event.target
        seen.set()


controller.add_event_listener(stream_event, EventType.STREAM)

found = seen.wait(timeout)

controller.remove_event_listener(stream_event)
controller.close()

if found:
    print("STREAM SUCCEEDED target={}".format(observed.get("target", "<unknown>")))
    sys.exit(0)

print("no STREAM reached SUCCEEDED within {}s".format(timeout))
sys.exit(1)
