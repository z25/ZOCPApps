#!/usr/bin/python

# IMPORTS
import sys
import pyttsx
import socket
import logging
from subprocess import Popen, PIPE
from shlex import split

from zocp import ZOCP

class SayNode(ZOCP):

    
    # Constructor
    def __init__(self, nodename=""):
        self.nodename = nodename
        super(SayNode, self).__init__()

        # INIT PYTTSX
        self.engine = pyttsx.init()
        #self.engine.setProperty('rate', 90)
        self.voices = self.engine.getProperty('voices')

        for voice in self.voices:
            print(voice.id,voice)
        

        self.engine.setProperty('voice', "en-scottish")
        #self.engine.say("text to speech is ready")
        #self.engine.runAndWait()
       
        # ZOCP STUFF
        self.set_name(self.nodename)
        # Register everything ..
        print("###########")
        self.register_string("textToSay", "hello", 'srw')
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
        new_value = self.capability[key]['value']

        if(type(new_value)== str):
            #self.engine.say(new_value)
            #self.engine.runAndWait()
            voiceParam = "-ven+f3 -k5 -s150"

            if(socket.gethostname()=="kwik"):
                voiceParam = "-s160 -ven+18 -z"
            elif(socket.gethostname()=="kwuk"):
                voiceParam = "-ven+f2 -k5 -s175 -z"
            elif(socket.gethostname()=="kwak"):
                voiceParam = "-ven+f4 -k5 -s170 -z"
        

            p1 = Popen(split('espeak '+voiceParam+' "'+new_value+'" --stdout'), stdout=PIPE)
            p2 = Popen(split("aplay -D sysdefault"), stdin=p1.stdout)

            
        
   

    
if __name__ == '__main__':
    #zl = logging.getLogger("zocp")
    #zl.setLevel(logging.DEBUG)

    z = SayNode("ttsNode@%s" % socket.gethostname())
    z.run()
    print("FINISH")


    

          
          



