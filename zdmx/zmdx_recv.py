#!/usr/bin/python

# IMPORTS
import json
import sys
import serial
import logging
# corectly set python path
#sys.path.append("../src/")
#sys.path.append("../../")
from zocp import ZOCP
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

    # INIT DMX
    mydmx = pysimpledmx.DMXConnection("/dev/tty.usbserial-EN134003")
    DMXchannel = 0
    DMXvalue = 0

    mydmx.setChannel(6,160)  # set DMX channel 
    mydmx.render()  

    
    def on_peer_signaled(self, peer, name, data, *args, **kwargs):
        print("#### on_peer_signaled")

        if self._running and peer:

            for sensor in data[2]:
                print("hier: ",sensor)

                if(sensor == "DMXchannel"):

                    self.DMXchannel = data[1]
                    print(data[1])

                if(sensor == "DMXvalue"):

                    print("Channel: ",self.DMXchannel)

                    self.DMXvalue = clamp(map(data[1],0,1,0,255),0,255)
                    self.mydmx.setChannel(self.DMXchannel,int(self.DMXvalue))  # set DMX channel 
                    self.mydmx.render()
                    print("######  Recieved message: channel: "+str(self.DMXchannel)+" value: "+str(self.DMXvalue))  


    def closeDMX(self):
        self.mydmx.close()

    def on_modified(self, peer, name, data, *args, **kwargs):
        print("#### on_modified")
        if self._running:
           

            if("DMXchannel" in data.keys() and "DMXvalue" in data.keys()):
                print(" we got you!")
                DMXchannel = int(data['DMXchannel']['value'])
                DMXvalue = clamp(map(data['DMXvalue']['value'],0,1,0,255),0,255)
                print("######  Recieved message: channel: "+str(DMXchannel)+" value: "+str(DMXvalue))
                #self.shout("ZOCP", json.dumps({ 'MOD' :self.capability}).encode('utf-8'))
                self.mydmx.setChannel(DMXchannel,int(DMXvalue))  # set DMX channel 
                self.mydmx.render()                         # render all of the above changes onto the DMX network

            if("DMXchannels" in data.keys() and "DMXvalues" in data.keys()):
                print(" MULTI DMX .... ")
                DMXchannels = data['DMXchannels']['value'].split("-")
                DMXvalues = data['DMXvalues']['value'].split("-")

                for i in range(0,len(DMXchannels)):
                    chan = int(DMXchannels[i])
                    val  = clamp(map(float(DMXvalues[i]),0,1,0,255),0,255) 
                    print("######  Recieved message: channel: "+str(chan)+" value: "+str(val))
                    self.mydmx.setChannel(chan,int(val))  # set DMX channel 

                self.mydmx.render()  

           
            
        else:
            print("not running...")



if __name__ == '__main__':
    zl = logging.getLogger("zocp")
    zl.setLevel(logging.DEBUG)

    z = DMXnode()
    z.set_name("ZOCP-DMX-Recieve")
    z.register_int('DMXuniverse', 1, access='srw', min=0, max=10, step=1)
    z.register_int('DMXchannel', 10, access='srw', min=0, max=511, step=1)
    z.register_float('DMXvalue', 0.4, access='srw', min=0, max=1, step=0.1)
    z.register_string('DMXchannels',"chan")
    z.register_string('DMXvalues',"val")
    z.start()
    
    z.run()
    z.closeDMX()
    print("FINISH")


    

          
          


