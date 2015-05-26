#!/usr/bin/python3
#
# ZOCP standard I/O entity
# Copyright (C) <2015> <Arnaud Loonstra>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
#
# Example:
# tail -f /var/log/syslog | zstdio.py

import sys
import zmq
import socket
import fcntl, os
from zocp import ZOCP

if __name__ == '__main__':
    hostname = socket.gethostname()
    z = ZOCP("zstdio@{0}".format(hostname))
    z.register_string("stdin", "", 're')
    z.start()

    # we need to set stdin to non blocking otherwise 
    # a read could potentially block
    flags = fcntl.fcntl(sys.stdin, fcntl.F_GETFL) 
    fcntl.fcntl(sys.stdin, fcntl.F_SETFL, flags | os.O_NONBLOCK)

    zpoller = zmq.Poller()
    zpoller.register(sys.stdin.fileno(), zmq.POLLIN)
    zpoller.register(z.inbox, zmq.POLLIN)
    def handle_stdin():
        input = sys.stdin.read(1024)
        sys.stdin.flush()
        if input:
            z.emit_signal("stdin", input)

    running = True
    try:
        while running:
                items = dict(zpoller.poll())
                if z.inbox in items and items[z.inbox] == zmq.POLLIN:
                    z.get_message()
                if sys.stdin.fileno() in items and items[sys.stdin.fileno()] == zmq.POLLIN:
                    handle_stdin()
    except Exception as e:
        running = False
    finally:
        zpoller.unregister(sys.stdin.fileno())
        zpoller.unregister(z.inbox)
        z.stop()

    print("FINISHED")
