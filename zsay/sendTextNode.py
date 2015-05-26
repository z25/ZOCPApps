#!/usr/bin/python

# IMPORTS
import sys
import socket
import logging
import json
import pprint

from zocp import ZOCP

class SayNode(ZOCP):

    
    # Constructor
    def __init__(self, nodename=""):
        self.nodename = nodename
        super(SayNode, self).__init__()

        # READ CONFIG FILE
        with open('texts.json') as data_file:    
            self.texts = json.load(data_file)

        print(self.texts)

        
       
        # ZOCP STUFF
        self.set_name(self.nodename)
        # Register everything ..
        print("###########")
        for name,data in self.texts.items():
            numTexts = len(data)
            self.register_int(name, 0, 'rws',0,numTexts,1)
            self.register_int(name+"length", numTexts, 'rw',0,numTexts,1)
            self.register_string(name+"_text", " ", 'rwe')

        #self.register_int("garcin", 0, 'srw')
        self.start()


    def on_peer_signaled(self, peer, name, data, *args, **kwargs):
        print("#### on_peer_signaled")
        if self._running and peer:
            print(data)
            print(peer)
            print(name)
            for sensor in data[2]:
                if(sensor):
                    self.receive_value(sensor)

    
    def on_modified(self, peer, name, data, *args, **kwargs):
        print("#### on_modified")
        if self._running and peer:
            print(data)
            print(peer)
            print(name)
            for key in data:
                if 'value' in data[key]:
                    self.receive_value(key)

    
    def receive_value(self, key):
        
        try:
            new_value = int(self.capability[key]['value'])
            text = self.texts[key][new_value]
            print("key ",key," value ",new_value," text ",text)

            self.emit_signal(key+"_text", text)
        except:
            print("error")
        

        
       
            
        
   

    
if __name__ == '__main__':
    #zl = logging.getLogger("zocp")
    #zl.setLevel(logging.DEBUG)

    z = SayNode("sendTextNode@%s" % socket.gethostname())
    z.run()
    print("FINISH")


    

          
          



