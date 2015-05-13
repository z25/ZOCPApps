#!/usr/bin/python3

from zocp import ZOCP
import socket
import logging

a=0

class ZEval(ZOCP):
    # Constructor
    def __init__(self, nodename=""):
        super(ZEval, self).__init__()
        self.eval_string = "a+1"
        self.set_name(nodename)
        self.register_string("eval", self.eval_string, "rw")
        self.register_int("a", a, "rws")
        self.register_int("out", 0, "e")
        self.start()
        self.run()

    def on_modified(self, peer, name, data, *args, **kwargs):
        if self._running and peer:
            if "eval" in data.keys() and 'value' in data["eval"]:
                self.new_eval(data["eval"]["value"])

    def new_eval(self, eval_string):
        try:
            eval(eval_string)
        except Exception as e:
            logger.error("Invalid eval string: {0}".format(e))
        else:
            self.eval_string = eval_string
            self.capability["eval"]['value'] = eval_string
                         
    def on_peer_signaled(self, peer, name, data, *args, **kwargs):
        if self._running and peer:
            self.eval_signal(data[0], data[1])

    def eval_signal(self, data, *args):
        print("EVAL SIG", data, args)
        try:
            a = args[0]
            out = eval(self.eval_string)
        except Exception as e:
            logger.error("Error during eval: {0}".format(e))
        else:
            self.emit_signal('out', out)


if __name__ == '__main__':
    logger = logging.getLogger("zocp")
    logger.setLevel(logging.DEBUG)

    z = ZEval("zeval@%s" % socket.gethostname())
    print("FINISH")

