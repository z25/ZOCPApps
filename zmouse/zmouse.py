import sys
import zmq
import socket
import struct
from zocp import ZOCP

XSIGN = 1<<4
YSIGN = 1<<5

if __name__ == '__main__':
    fd = open('/dev/input/mouse0','rb')
    fn = fd.fileno()

    z = ZOCP()
    hostname = socket.gethostname()
    z.set_name("mouse@{0}".format(hostname))
    z.start()

    position = [0., 0.]
    button = [False, False, False]

    z.register_vec2f("Position", position, 're')
    z.register_bool("Left button", button[0], 're')
    z.register_bool("Right button", button[1], 're')
    z.register_bool("Middle button", button[2], 're')

    zpoller = zmq.Poller()
    zpoller.register(fd, zmq.POLLIN)
    zpoller.register(z.inbox, zmq.POLLIN)

    def handle_mouse_in():
        (buttons, dx, dy) = struct.unpack('BBB', fd.read(3))

        this_button = (buttons & 1 != 0)
        if this_button != button[0]:
            button[0] = this_button
            z.emit_signal("Left button", this_button)
        this_button = (buttons & 2 != 0)
        if this_button != button[1]:
            button[1] = this_button
            z.emit_signal("Right button", this_button)
        this_button = (buttons & 4 != 0)
        if this_button != button[2]:
            button[2] = this_button
            z.emit_signal("Middle button", this_button)

        if buttons & XSIGN:
            dx-=256
        if buttons & YSIGN:
            dy-=256

        if dx != 0 or dy != 0:
            position[0] += dx
            position[1] += dy
            z.emit_signal("Position", position)


    running = True
    try:
        while running:
            items = dict(zpoller.poll())
            if z.inbox in items and items[z.inbox] == zmq.POLLIN:
                z.get_message()
            if fn in items and items[fn] == zmq.POLLIN:
                handle_mouse_in()
    except Exception as e:
        running = False
    finally:
        zpoller.unregister(fd)
        fd.close()
        zpoller.unregister(z.inbox)
        z.stop()

    print("FINISHED")
