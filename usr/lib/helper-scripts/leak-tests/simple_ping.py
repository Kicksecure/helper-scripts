#!/usr/bin/python3 -u

## Copyright (C) 2012 - 2020 ENCRYPTED SUPPORT LP <adrelanos@riseup.net>
## See the file COPYING for copying conditions.

# Since it will be useful to know something about the script,
# for the later tests, the terms are defined here:
# (A discussion of Python language structure is beyond
# the scope of this document)

# [1] http://en.wikipedia.org/wiki/Ipv4
# [2] http://en.wikipedia.org/wiki/Internet_Control_Message_Protocol
# [3] http://en.wikipedia.org/wiki/IP_routing
# [4] http://en.wikipedia.org/wiki/Ping
# [5] http://en.wikipedia.org/wiki/Internet_Control_Message_Protocol#List_of_permitted_control_messages_.28incomplete_list.29
# [6] http://www.secdev.org/projects/scapy/doc/usage.html#send-and-receive-packets-sr
# [7] http://www.secdev.org/projects/scapy/doc/usage.html#stacking-layers

import sys
from scapy.all import *

# define the target gateway & data payload
target = "10.152.152.10"
#target = "45.33.32.156"

data = "testing"

# define packets
# These define two variables, that are set to the object types IP
# and ICMP respectively. These objects in Scapy define the protocol
# type for IP (default IPv4) [1] and ICMP [2] respectively.
# And will send packets on the wire of these types when used.
ip = IP()
icmp = ICMP()

# define packet parameters
ip.dst = target

# IP packets are used for routing [3] between networks on the Internet.
# So, we assign the destination (dst) in the IP portion of the
# packet we are going to assemble and send out.
icmp.type = 8
icmp.code = 0

# Defines the type of ICMP message to send out. The ..8 type.. is
# a type defined as ..echo request.., e.g. a simple ping [4].
# See a list here of  various types of ICMP [5] messages here.

# The sr1() [6] command will ..send and receive network traffic,
# returning the 1st packet received...
# The notation of ..ip/icmp/data.. is the notation for encapsulation
# of various instances of networking protocols [7].
# Read it right to left: ..data encapsulated inside an ICMP message
# and encapsulated inside an IP datagram...
test_ping = sr1(ip/icmp/data)

if isinstance(test_ping, types.NoneType):
        print("No response")
else:
# Prints a short report on the packet received (if any).
        test_ping.summary()
