#/usr/bin/env python3
#
# ZOCP Video Player
# Copyright (c) 2014 Stichting z25.org
# Copyright (c) 2014 Arnaud Loonstra <arnaud@sphaero.org>
#
# ZOCP Video Player is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Use the following pipeline for a sender:
# gst-launch-1.0 -v videotestsrc ! video/x-raw,frame-rate=10/1 ! x264enc speed-preset=1 tune=zero-latency byte-stream=true intra-refresh=true option-string="bframes=0:force-cfr:no-mbtree:sync-lookahead=0:sliced-threads:rc-lookahead=0" ! video/x-h264,profile=high ! rtph264pay config-interval=1 ! udpsink host=127.0.0.1 port=5000
#
# Debian dependencies:
# apt-get install gstreamer1.0-plugins-bad gstreamer1.0-plugins-good gstreamer1.0-tools python3-gst-1.0 gstreamer1.0-libav gir1.2-gstreamer-1.0 gir1.2-gst-plugins-base-1.0

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst
print(Gst.version())

from zocp import ZOCP
import zmq
import socket


pls = ["file:///home/arnaud/Videos/fingers.mov"]
count = 0

def bus_call(bus, msg, *args):
    if msg.type == Gst.MessageType.EOS:
        print("End-of-stream")
        update_uri()
        #loop.quit()
        return True
    elif msg.type == Gst.MessageType.ERROR:
        print(msg.parse_error())
        loop.quit()
        return True
    return True

def update_uri(*args, **kwargs):
    global count
    count = (count+1)%len(pls)
    pipeline.set_state(Gst.State.READY)
    glimagesink.set_state(Gst.State.PAUSED)
    videosrc.set_property("uri", pls[count])
    pipeline.set_state(Gst.State.PLAYING)
    glimagesink.set_state(Gst.State.PLAYING)
    return True

def on_pad_added(element, pad, *args):
    #print(element, pad, args)
    print(pad.is_linked(), element, pad, args)
    if not pad.is_linked():
        pad.link(args[0].get_static_pad("sink")) #args[0])

def zocp_handle(*args, **kwargs):
    print("bah")
    z.run_once()
    if z.capability['quit']['value']:
        loop.quit()
    print("END run once")
    return True


if __name__ == "__main__":
    GObject.threads_init()
    ret = Gst.StateChangeReturn
    # initialization
    loop = GObject.MainLoop()
    Gst.init(None)
    # create elements
    pipeline = Gst.Pipeline()
    
    # create gst elements
    videosrc = Gst.ElementFactory.make('uridecodebin', 'videosrc0')
    glimagesink = Gst.ElementFactory.make('glimagesink', "glimagesink0")
    
    # setup the pipeline
    #videosrc.set_property("video-sink", glimagesink)
    videosrc.set_property("uri", pls[count])
    glimagesink.set_locked_state(True)
    
    # we add a message handler
    bus = pipeline.get_bus()
    bus.add_watch(0, bus_call, loop) # 0 == GLib.PRIORITY_DEFAULT 
    
    # we add all elements into the pipeline
    pipeline.add(videosrc)
    pipeline.add(glimagesink)
    
    # we link the elements together
    #videosrc.link(glimagesink)
    videosrc.connect("pad-added", on_pad_added, glimagesink)

    z = ZOCP()
    z.set_name("zvidplyr@{0}".format(socket.gethostname()))
    z.register_bool("quit", False, access='rw')
    z.register_vec2f("top_left", (-1.0, 1.0), access='rw', step=[0.01, 0.01])
    z.register_vec2f('top_right', (1.0, 1.0), access='rw', step=[0.01, 0.01])
    z.register_vec2f('bottom_right', (1.0, -1.0), access='rw', step=[0.01, 0.01])
    z.register_vec2f('bottom_left', (-1.0, -1.0), access='rw', step=[0.01, 0.01])
    z.register_string("playlist", "test.h264", access="rws")
    z.register_bool("fade", False, access="rw")
    z.register_bool("pause", False, access="rw")
    z.register_bool("stop", False, access="rw")
    z.register_bool("stop", False, access="rw")
    z.start()
    
    # listen to the zocp inbox socket
    GObject.io_add_watch(
        z.inbox.getsockopt(zmq.FD), 
        GObject.PRIORITY_DEFAULT, 
        GObject.IO_IN, zocp_handle
    )
    GObject.timeout_add(4000, update_uri)
    
    pipeline.set_state(Gst.State.PLAYING)
    glimagesink.set_state(Gst.State.PLAYING)
    try:
        loop.run()
    except Exception as e:
        print(e)
    finally:
        z.stop()

    pipeline.set_state(Gst.State.NULL)

