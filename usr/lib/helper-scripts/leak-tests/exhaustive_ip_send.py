#!/usr/bin/python3 -u

## Copyright (C) 2012 - 2020 ENCRYPTED SUPPORT LP <adrelanos@riseup.net>
## See the file COPYING for copying conditions.

import sys
from scapy.all import *

#define the target gateway & data payload
target = "scanme.nmap.org"
#target = "45.33.32.156"

data = "testing"

#define packet
ip = IP()

#define packet parameters
ip.dst = target

#loop through all IP packet types
for ip_type in range(0,255):
        ip.proto = ip_type
        send(ip/data)
