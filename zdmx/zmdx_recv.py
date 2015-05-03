#!/usr/bin/python

# IMPORTS
import json
import sys
import serial
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

    
    def on_modified(self, data, peer=None):
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
    #z = ZOCP()
    z = DMXnode()
    z.set_node_name("ZOCP-DMX-Recieve")
    z.register_int('DMXuniverse', 1, access='rw', min=0, max=10, step=1)
    z.register_int('DMXchannel', 10, access='rw', min=0, max=511, step=1)
    z.register_float('DMXvalue', 0.4, access='rw', min=0, max=1, step=1)
    z.register_string('DMXchannels',"chan")
    z.register_string('DMXvalues',"val")
    
    z.run()
    z.stop()
    print("FINISH")


    

          
          


