#!/usr/bin/python

# IMPORTS
import json
import sys
import serial
import logging

from zocp import ZOCP
from pprint import pprint
# DMX STUFF
import pysimpledmx

def map(value, istart, istop,  ostart,  ostop):
    return ostart + (ostop - ostart) * ((value - istart) / (istop - istart))

def clamp(n, minn, maxn):
    if n < minn:
        return minn
    elif n > maxn:
        return maxn
    else:
        return n

class DMXnode(ZOCP):

    
    # Constructor
    def __init__(self, nodename=""):
        self.nodename = nodename
        super(DMXnode, self).__init__()

        # INIT DMX
        #mydmx = pysimpledmx.DMXConnection("/dev/ttyUSB0")
        self.mydmx = pysimpledmx.DMXConnection("/dev/tty.usbserial-EN134003")
        

        # READ CONFIG FILE
        with open('lights.json') as data_file:    
            self.lamps = json.load(data_file)

        pprint(self.lamps)
        
        # ZOCP STUFF
        self.set_name(self.nodename)
        # Register everything ..
        print("###########")
        for name,data in self.lamps.items():

            print(name)
            if(len(data["DMXparameters"]) == 1):
                self.register_int(name, 0, 'rws',0,255,1)
            elif(len(data["DMXparameters"]) == 2):
                self.register_vec2f(name, [0,0], 'rws',0,255,1)
            elif(len(data["DMXparameters"]) == 3):
                self.register_vec3f(name, [0,0,0], 'rws',0,255,1)
            elif(len(data["DMXparameters"]) == 4):
                self.register_vec4f(name, [0,0,0,0], 'rws',0,255,1)
            
            elif(len(data["DMXparameters"]) == 5):
                self._register_param(name, [0,0,0,0,0],'vec5f','rws',0,255,1)
            
            #register_vec4f(self, name, vec4f, access='r', min=None, max=None, step=None)


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

    def newZoomRGBlight(self,startAdress,values):
        # RGB
        self.mydmx.setChannel(startAdress,int(values[0])) 
        self.mydmx.setChannel(startAdress+1,int(values[1])) 
        self.mydmx.setChannel(startAdress+2,int(values[2])) 

        # Strobe
        self.mydmx.setChannel(startAdress+5,255) 

        #Master & ZOOM
        self.mydmx.setChannel(startAdress+6,int(values[3])) 
        self.mydmx.setChannel(startAdress+7,int(values[4]))

    def receive_value(self, key):
        new_value = self.capability[key]['value']
        startAdress = self.lamps[key]["DMXadress"]

        # It is a list so it is a light with multiple parameters
        if(type(new_value) is list):

            if(key == 'RGBZOOM5' or key == 'RGBZOOM6'):
                self.newZoomRGBlight(startAdress,new_value)

            else:
                for n in new_value:
                    print("n:",n)
                    self.mydmx.setChannel(startAdress,int(n)) 
                    startAdress += 1
        # Light with single value
        else:
            #print("it is NOT list",new_value)
            self.mydmx.setChannel(startAdress,int(new_value))  # set DMX channel 
        
        self.mydmx.render()
        #print("######  Recieved message: channel: "+str(self.lamps[key]["DMXadress"])+" value: "+str(new_value))  
        
    def closeDMX(self):
        self.mydmx.close()

    
if __name__ == '__main__':
    #zl = logging.getLogger("zocp")
    #zl.setLevel(logging.DEBUG)

    z = DMXnode("ZOCP-DMX-Recieve-Config")
    z.run()
    z.closeDMX()
    print("FINISH")


    

          
          


