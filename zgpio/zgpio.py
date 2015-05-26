#!/usr/bin/python

import zmq
from quick2wire.gpio import pins, In, Out, Rising, Falling
from zocp import ZOCP
import logging

if __name__ == '__main__':
    zl = logging.getLogger("zocp")
    zl.setLevel(logging.DEBUG)

    z = ZOCP("ZOCP-GPIO")
    z.register_bool("myBool", True, 'rwe')
    z.register_float("myFloat", 2.3, 'rws', 0, 5.0, 0.1)
    z.register_int('myInt', 10, access='rwes', min=-10, max=10, step=1)
    z.register_percent('myPercent', 12, access='rw')
    z.register_vec2f('myVec2', [0,0], access='rwes')

    # register pins
    pin1 = pins.pin(0, direction=In, interrupt=Rising)
    pin2 = pins.pin(1, direction=In, interrupt=Falling)
    
    def handle_pin(pin):
        logging.debug("handle pin {0}".format(pin))
        with pin:
            logging.debug("pin {0}:{1}".format(pin, pin.value)

    poller = zmq.Poller()
    poll.register(z.inbox, zmq.POLLIN)
    poll.register(pin1.fileno(), zmq.POLLIN)
    poll.register(pin2.fileno(), zmq.POLLIN)
    z.start()
    z.running = True #is this needed?
    while True:
        try:
            items = dict(poller.poll())
            while(len(items) > 0):
                for fd, ev in items.items():
                    if z.inbox == fd and ev == zmq.POLLIN:
                        z.get_message()
                    if pin1.fileno() == fd and ev == zmq.POLLIN:
                        handle_pin(pin1)
                    if pin2.fileno() == fd and ev == zmq.POLLIN:
                        handle_pin(pin2)
        except (KeyboardInterrupt, SystemExit):
            break

    z.stop()
    print("FINISH")
