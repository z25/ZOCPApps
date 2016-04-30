#!/usr/bin/python3
#
# ZOCP Inotify Actor
# Copyright (C) <2016> <Arnaud Loonstra>
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

import sys
import zmq
import socket
import fcntl
import os
import array
import struct
import pyinotify
import termios
from zocp import ZOCP
import logging

if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    hostname = socket.gethostname()
    z = ZOCP("zinotify@{0}".format(hostname))
    z.register_string("watchdir", "/tmp", "rw")
    z.register_string("file", "", 're')
    z.start()

    # setup inotify
    i = pyinotify.INotifyWrapper.create()
    ifd = i._inotify_init()
    # add a directory to watch
    iwd = i.inotify_add_watch( ifd, z.get_value('watchdir'), pyinotify.IN_DELETE )

    zpoller = zmq.Poller()
    zpoller.register(ifd, zmq.POLLIN)
    zpoller.register(z.inbox, zmq.POLLIN)
    
    def handle_modified(peer, name, data, *args, **kwargs):
        global iwd
        global ifd
        print(data, name, "watchdir" in data.keys())
        if "watchdir" in data.keys():
            logger.debug("watchdir modified to {1} by {0}".format(peer, data))
            # stop current watch
            i.inotify_rm_watch(ifd, iwd)
            # start new watch
            iwd = i.inotify_add_watch( ifd, z.get_value('watchdir'), pyinotify.IN_DELETE )
    z.on_modified = handle_modified
 
    def handle_inotify():
        buf = array.array('i', [0])
        if fcntl.ioctl(ifd, termios.FIONREAD, buf, 1) == -1: # get length of buffer
            logger.error('some ioctl -1 error')
            running = False
            return
        length = buf[0]
        # read data
        # todo we should loop over the data!
        recv = os.read(ifd, length)
        logger.debug("handle_inotify: recveived length {0}".format(len(recv)))
        rwd, evmask, cookie, data_length = struct.unpack('iIII', recv[0:16])
        if rwd != iwd:
            logger.debug("watch descriptor doesn't match: %d is not %d" %(rwd, iwd))
            return
        data, = struct.unpack('%ds' %data_length, recv[16:length])
        # since data is a string this is a hack to remove the null bytes
        data = data.partition(b'\0')
        if data[0]:
            z.emit_signal("file", data[0].decode('utf-8'))

    running = True
    try:
        while running:
                items = dict(zpoller.poll())
                if z.inbox in items and items[z.inbox] == zmq.POLLIN:
                    z.get_message()
                if ifd in items and items[ifd] == zmq.POLLIN:
                    handle_inotify()

    except Exception as e:
        print(e)
        running = False
    finally:
        zpoller.unregister(ifd)
        zpoller.unregister(z.inbox)
        z.stop()

    print("FINISHED")

