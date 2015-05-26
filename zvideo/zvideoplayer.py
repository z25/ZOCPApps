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
# Debian dependencies:
# apt-get install gstreamer1.0-plugins-bad gstreamer1.0-plugins-good gstreamer1.0-tools python3-gst-1.0 gstreamer1.0-libav gir1.2-gstreamer-1.0 gir1.2-gst-plugins-base-1.0
#
# There's a bug in gstreamer-vaapi <0.5.10 see: https://bugzilla.gnome.org/show_bug.cgi?id=743035
# workaround is export LIBVA_DRIVER_NAME=bla to make vaapi fail en revert to software decoding

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst
print(Gst.version())

from zocp import ZOCP
import zmq
import socket

import argparse
import sys
import os

import platform
import re

# https://raw.githubusercontent.com/adafruit/Adafruit_Python_GPIO/master/Adafruit_GPIO/Platform.py
def pi_version():
    """Detect the version of the Raspberry Pi.  Returns either 1, 2 or
    None depending on if it's a Raspberry Pi 1 (model A, B, A+, B+),
    Raspberry Pi 2 (model B+), or not a Raspberry Pi.
    """
    # Check /proc/cpuinfo for the Hardware field value.
    # 2708 is pi 1
    # 2709 is pi 2
    # Anything else is not a pi.
    with open('/proc/cpuinfo', 'r') as infile:
        cpuinfo = infile.read()
    # Match a line like 'Hardware   : BCM2709'
    match = re.search('^Hardware\s+:\s+(\w+)$', cpuinfo,
                      flags=re.MULTILINE | re.IGNORECASE)
    if not match:
        # Couldn't find the hardware, assume it isn't a pi.
        return None
    if match.group(1) == 'BCM2708':
        # Pi 1
        return 1
    elif match.group(1) == 'BCM2709':
        # Pi 2
        return 2
    else:
        # Something else, not a pi.
        return None


class GstZOCP(ZOCP):
    
    def __init__(self, pls=None, *args, **kwargs):
        super(GstZOCP, self).__init__(*args, **kwargs)
        GObject.threads_init()
        self.loop = GObject.MainLoop()
        Gst.init(None)
        if pls == None:
            pls = ""
            #pls = "file:///home/people/arnaud/Videos/tordinaire-youtubeHD.mp4" 
        #pls = "file:///home/pi/test3.h264,file:///home/pi/tordinaire-youtubeHD.mp4"
        #pls = "file:///home/people/arnaud/Videos/test.h264,file:///home/people/arnaud/Videos/test2.h264"
        self.count = 0
        # create elements
        self._prerolled = False
        self.playbin = Gst.ElementFactory.make('playbin', 'playbin0')
        self.glcolorconv = Gst.ElementFactory.make("glcolorscale", "glcolorconv0")
        self.glshader = Gst.ElementFactory.make("glshader", "glshader0")
        self.glimagesink = Gst.ElementFactory.make('glimagesink', "glimagesink0")
        self.sinkbin = Gst.Bin()

        # setup the pipeline
        #videosrc.set_property("video-sink", glimagesink)
        #self.playbin.set_property("uri", pls.split(',')[self.count])
        #self.glimagesink.set_locked_state(True)
        self.sinkbin.add(self.glcolorconv)
        self.sinkbin.add(self.glshader)
        self.sinkbin.add(self.glimagesink)
        
        # we add a message handler
        self.bus = self.playbin.get_bus()
        self.bus.add_watch(0, self.bus_call, self.loop) # 0 == GLib.PRIORITY_DEFAULT 
        
        # we link the elements together
        self.glshader.link(self.glimagesink)
        self.glcolorconv.link(self.glshader)
        self.glshader.link(self.glimagesink)
        ghostpad = Gst.GhostPad.new("sink", self.glcolorconv.get_static_pad("sink"))
        self.sinkbin.add_pad(ghostpad)

        #self.playbin.connect("pad-added", self.on_pad_added, self.sinkbin)
        #self.playbin.connect("drained", self.on_drained)
        #self.playbin.connect("about-to-finish", self.update_uri)
        
        # set properties of elements
        self.glshader.set_property("location", "shader.glsl")
        self.glshader.set_property("vars", "float alpha = float(1.);")
        self.glshader.set_property("preset", "preset.glsl")
        self.playbin.set_property("video-sink",self.sinkbin)
        if pi_version():
            # force rpi analog audio output
            self.audiosink = Gst.ElementFactory.make('omxanalogaudiosink', "omxanalogaudiosink0")        
            self.playbin.set_property("audio-sink",self.audiosink)

        self.set_name("zvidplyr@{0}".format(socket.gethostname()))
        self.register_bool("quit", False, access='rw')
        #self.register_vec2f("top_left", (-1.0, 1.0), access='rw', step=[0.01, 0.01])
        #self.register_vec2f('top_right', (1.0, 1.0), access='rw', step=[0.01, 0.01])
        #self.register_vec2f('bottom_right', (1.0, -1.0), access='rw', step=[0.01, 0.01])
        #self.register_vec2f('bottom_left', (-1.0, -1.0), access='rw', step=[0.01, 0.01])
        self.register_string("playlist", pls, access="rws")
        self.register_bool("loop", True, access="rws")
        self.register_bool("fade", True, access="rws")
        self.register_bool("next", False, access="rws")
        self.register_bool("auto_next", True, access="rws")
        self.register_vec3f("fade_color", (1,0,0), access="rws")
        self.register_bool("pause", False, access="rws")
        self.register_bool("stop", False, access="rws")
        
        self._fade_val = 1.0
    
    def pause_vid(self, p):
        if self.playbin.get_state(0)[1] == Gst.State.NULL:
            print("No URI configured")
            return

        if p:
            print("pause", p)
            self.playbin.set_state(Gst.State.PAUSED)
        else:
            self.playbin.set_state(Gst.State.PLAYING)

    def stop_vid(self, p):
        #if self.playbin.get_state(0)[1] == Gst.State.NULL:
        #    print("No URI configured")
        #    return
        if p:
            if self.playbin.get_state(0)[1] == Gst.State.PLAYING:
                self.playbin.set_state(Gst.State.PAUSED)
                self.playbin.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, 0)
        else:
            self.playbin.set_state(Gst.State.PLAYING)
     
    def fade_vid(self, f):
        if f and self._fade_val == 0.:
            GObject.timeout_add(10, self._fade, f)
        elif self._fade_val == 1.0:
            GObject.timeout_add(10, self._fade, f)        

    def loop_vid(self, *args):
        print("LOOP")
        # https://lazka.github.io/pgi-docs/#Gst-1.0/flags.html#Gst.SeekFlags
        flags = Gst.SeekFlags.SEGMENT | Gst.SeekFlags.FLUSH
        self.playbin.seek_simple (Gst.Format.TIME, flags, 0);

    def bus_call(self, bus, msg, *args):
        """
        handling messages on the gstreamer bus
        """
        if msg.type == Gst.MessageType.SEGMENT_DONE or msg.type == Gst.MessageType.EOS:
            print("SEG DONE")
            if not self.capability["loop"]["value"]:
                if self.capability["auto_next"]["value"]:
                    self.update_uri()           # get next file from playlist
                else:
                    self.stop_vid(True)       
            else:
                self.loop_vid()
            return True
        elif msg.type == Gst.MessageType.ASYNC_DONE:
            if not self._prerolled:
                print("Initial seek ...");
                flags = Gst.SeekFlags.FLUSH | Gst.SeekFlags.SEGMENT
                self.playbin.seek_simple (Gst.Format.TIME, flags, 0);
                self._prerolled = True
        elif msg.type == Gst.MessageType.ERROR:
            print(msg.parse_error())
            self.loop.quit()            # quit.... (better restart app?)
            return True
        return True

    def update_uri(self, *args, **kwargs):
        """
        set next file from playlist
        """
        pls = self.capability["playlist"]["value"].split(',')
        self.count = (self.count+1)%len(pls)
        next_vid = pls[self.count]
        print(next_vid, self.playbin.get_state(0)[1])
        if next_vid:  # set next video if there is any
            self.playbin.set_state(Gst.State.READY)
            self.playbin.set_property("uri", next_vid)
            # seek to beginning
            #self.playbin.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, 0)
            self.stop_vid(False)
            #self.playbin.set_state(Gst.State.PLAYING)
        else:
            self.stop_vid(True)
            self.playbin.set_state(Gst.State.NULL)
        return True

    def on_pad_added(self, element, pad, target, *args):
        """
        called when we can link to the sink
        """
        print(element, pad, target)
        if not pad.is_linked():
            pad.link(target.get_static_pad("sink")) #args[0])

    def zocp_handle(self, *args, **kwargs):
        self.run_once()
        if self.capability['quit']['value']:
            self.loop.quit()
        return True


    def on_modified(self, peer, name, data, *args, **kwargs):
        # capability modified by SET, check if the value changed
        if self._running and peer:
            for key in data:
                if 'value' in data[key]:
                    self.receive_value(key)


    def on_peer_signaled(self, peer, name, data, *args, **kwargs):
        # receive a value from a signal
        if self._running and peer:
            for sensor in data[2]:
                if(sensor):
                    self.receive_value(sensor)


    def receive_value(self, key):
        # value changed by either SET or SIG
        new_value = self.capability[key]['value']

        if self._running:
            if key == "pause":
                self.pause_vid(new_value)
            elif key == "stop":
                self.stop_vid(new_value)
            elif key == "next":
                if new_value:
                    self.update_uri()
            elif key == "fade":
                self.fade_vid(new_value)
            elif key == "fade_color":
                pass
            elif key == "playlist":
                # update uri
                if self.capability["stop"]["value"] or self.capability["pause"]["value"]:
                    self.update_uri()
            else:
                print("don't know", key, new_value)

        
    def run(self):
        # listen to the zocp inbox socket
        GObject.io_add_watch(
            self.inbox.getsockopt(zmq.FD), 
            GObject.PRIORITY_DEFAULT, 
            GObject.IO_IN, self.zocp_handle
        )
        #GObject.timeout_add(2000, self.update_uri)
        self.start()

        #self.playbin.set_state(Gst.State.PLAYING)
        self.update_uri()

        try:
            self.loop.run()
        except Exception as e:
            print(e)
        finally:
            self.stop()
        
        self.playbin.set_state(Gst.State.NULL)

    def _fade(self, f):
        color = self.capability["fade_color"]["value"]
        self.glshader.set_property("vars", "float alpha = float({0}); vec3 color = vec3({1},{2},{3});".
            format(self._fade_val, color[0], color[1], color[2]))
        if f:
            self._fade_val += 0.01
            if self._fade_val >= 1.0:
                self._fade_val = 1.0
                print("FADED IN")
                return False
        else:
            self._fade_val -= 0.01
            if self._fade_val <= .0:
                self._fade_val = .0
                print("FADED OUT")
                return False
        return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Play videofiles controlled through ZOCP.')
    parser.add_argument('files', metavar='file', type=str, nargs=argparse.REMAINDER,
                   help='files to add to the playlist')
    args = parser.parse_args()

    pls = ""
    for file in args.files:
        if not os.path.isfile(file):
            print("File {0} doesn't exist".format(file))
            sys.exit(1)
        pls += "file://{0},".format(os.path.abspath(file))

    pls = pls[:-1]      # remove final ','
    print(pls)
    player = GstZOCP(pls)
    player.run()
