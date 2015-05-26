#!/usr/bin/python

'''
    use subprocess to triggen the say command to do Text to speech
    Works on OSX out of the box.
    On Ubuntu do apt-get install gnustep-gui-runtime

'''

# IMPORTS
import sys
import subprocess

from zocp import ZOCP

def map(value, istart, istop,  ostart,  ostop):
    return ostart + (ostop - ostart) * ((value - istart) / (istop - istart))

def clamp(n, minn, maxn):
    if n < minn:
        return minn
    elif n > maxn:
        return maxn
    else:
        return n

class SayNode(ZOCP):

    
    # Constructor
    def __init__(self, nodename=""):
        self.nodename = nodename
        super(SayNode, self).__init__()

        # INIT DMX
       
        # ZOCP STUFF
        self.set_name(self.nodename)
        # Register everything ..
        print("###########")
        self.register_string("text to say", "bla", 'srw')
        subprocess.call('say "init"', shell=True)
        self.start()


    def on_peer_signaled(self, peer, name, data, *args, **kwargs):
        print("#### on_peer_signaled")
        if self._running and peer:
            for sensor in data[2]:
                if(sensor):
                    self.receive_value(sensor)

    
    def on_modified(self, peer, name, data, *args, **kwargs):
        print("#### on_modified")
        if self._running and peer:
            for key in data:
                if 'value' in data[key]:
                    self.receive_value(key)

    
    def receive_value(self, key):
        new_value = self.capability[key]['value']

        if(type(new_value)== str):
            toSay = "say "+new_value
            subprocess.call(toSay, shell=True)
        
   

    
if __name__ == '__main__':
    #zl = logging.getLogger("zocp")
    #zl.setLevel(logging.DEBUG)

    z = SayNode("SAYnode")
    z.run()
    print("FINISH")


    

          
          


