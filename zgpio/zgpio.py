#!/usr/bin/python

import zmq
from quick2wire.gpio import pins, In, Out, Rising, Falling
from zocp import ZOCP
import logging

class gpio(object):

    def __init__(self, pin, direction, value):
        self.pin = pin
        self.direction = direction
        self.value = value
        self.open_gpio()


    def export_pin(self):
        export_file = open("/sys/class/gpio/export", "w")
        export_file.write(str(self.pin))
        export_file.close()

    def unexport_pin(self):
        unexport_file = open("/sys/class/gpio/unexport", "w")
        unexport_file.write(str(self.pin))
        unexport_file.close()

    def set_pin_irection(self):
        direction_file = open("/sys/class/gpio/gpio" + str(self.pin) + "/direction", "w")
        direction_file.write(self.direction) #in or out
        direction_file.close()

    def get_pin_direction(self):
        direction_file = open("/sys/class/gpio/gpio" + str(self.pin) + "/direction", "r")
        self.direction = direction_file.read(1)
        direction_file.close()
        return self.direction

    def set_pin_value(self,v):
        self.value = v
        value_file = open("/sys/class/gpio/gpio" + str(self.pin) + "/value", "w")
        value_file.write(str(self.value))
        value_file.close()

    def get_pin_value(self):
        value_file = open("/sys/class/gpio/gpio" + str(self.pin) + "/value", "r")
        self.value = value_file.read(1)
        value_file.close()
        return self.value

    def get_pin(self):
        return self.pin

    def open_gpio(self):
        self.export_pin()
        self.pin_direction()

    def close_gpio(self):
        self.unexport_pin()



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
