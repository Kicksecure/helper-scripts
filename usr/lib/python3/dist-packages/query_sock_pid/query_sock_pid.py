#!/usr/bin/python3 -su

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

# pylint: disable=broad-exception-caught

"""
query_sock_pid.py: Library that allows determining the PID of the process
acting as a server for a particular UNIX socket.
"""

import socket
import struct


def query_sock_pid(sock_path: str) -> str | None:
    """
    Given a path to a UNIX socket, returns the PID of the program listening on
    it.
    """

    try:
        with socket.socket(
            socket.AF_UNIX, socket.SOCK_STREAM | socket.SOCK_CLOEXEC
        ) as sock:
            sock.settimeout(0.5)
            sock.connect(sock_path)
            struct_fmt: str = "=iII"
            rslt_buf: bytes = sock.getsockopt(
                socket.SOL_SOCKET,
                socket.SO_PEERCRED,
                struct.calcsize(struct_fmt),
            )
            pid: int
            pid, _, _ = struct.unpack(struct_fmt, rslt_buf)
            return str(pid)
    except Exception:
        ## Logging not desirable here, socket may have been closed or deleted.
        return None
