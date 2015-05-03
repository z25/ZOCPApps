import sys
import zmq
import socket
import termios, fcntl, os
from zocp import ZOCP


if __name__ == '__main__':
    # see https://docs.python.org/2/faq/library.html#how-do-i-get-a-single-keypress-at-a-time
    fd = sys.stdin.fileno()

    oldterm = termios.tcgetattr(fd)
    newattr = termios.tcgetattr(fd)
    newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
    termios.tcsetattr(fd, termios.TCSANOW, newattr)

    oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

    z = ZOCP()
    hostname = socket.gethostname()
    z.set_name("keyboard@{0}".format(hostname))
    z.register_string("Keyboard", "", 'r')
    zpoller = zmq.Poller()
    zpoller.register(sys.stdin, zmq.POLLIN)
    zpoller.register(z.inbox, zmq.POLLIN)
    def handle_key_in():
        input = sys.stdin.read(1)
        print("KEYBOARD IN: {0}".format(input))
        z.register_string("Keyboard", input, 'r')

    running = True
    while running:
        try:
            items = dict(zpoller.poll())
            if z.inbox in items and items[z.inbox] == zmq.POLLIN:
                z.run_once()
            if sys.stdin.fileno() in items and items[sys.stdin.fileno()] == zmq.POLLIN:
                handle_key_in()
        except (KeyboardInterrupt, SystemExit):
                running = False
                break

    zpoller.unregister(sys.stdin)
    zpoller.unregister(z.inbox)
    z.stop()
    termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
    fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
    print("FINISHED")
