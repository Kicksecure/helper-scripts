#!/usr/bin/python

## This file is part of Whonix.
## Copyright (C) 2012 - 2014 Patrick Schleizer <adrelanos@riseup.net>
## See the file COPYING for copying conditions.

import sys
import stem

from stem import connection
from stem.control import Controller

try:
  if len(sys.argv) < 4:
      print 'Syntax error. %s' % sys.argv
      sys.exit(255)

  a=str(sys.argv[1])
  p=int(sys.argv[2])

  with Controller.from_port(address = a, port = p) as controller:

    if str(sys.argv[3]) == "1":
      controller.authenticate()

    circuit_established = controller.get_info("status/circuit-established")

    ## Possible answer, if established:
    ## 1

    ## Possible answer, if not established:
    ## 0

    print "%s" % (circuit_established)

    exit_code = 0

except ValueError as e:
  print e
  exit_code=255
except NameError as e:
  print 'Name error: %s' % e
  exit_code=255
except connection.AuthenticationFailure as e:
  print 'Unable to authenticate: %s' % e
  exit_code=255
except stem.SocketError as e:
  print 'Socket error: %s' % e
  exit_code=255
except stem.ProtocolError as e:
  print 'Protocol error: %s' % e
  exit_code=255
except stem.InvalidArguments as e:
  print 'Invalid Arguments: %s' % e
  exit_code=255

sys.exit(exit_code)
