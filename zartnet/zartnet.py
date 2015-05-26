#!/usr/bin/python

# IMPORTS
import json
import sys
# corectly set python path
#sys.path.append("../src/")
#sys.path.append("../../")
from zocp import ZOCP 
from artnet import ArtnetController, DmxPort

class Artnetnode(ZOCP):

    # INIT Artnet
    ac = ArtnetController("pyartnet-setdmx") 
    dp = DmxPort(0, DmxPort.INPUT)
    ac.add_port(dp)

    def on_modified(self, data, peer=None):
        if self._running:
            DMXchannel = self.capability['DMXchannel']['value']
            DMXvalue = self.capability['DMXvalue']['value']
            DMXvalue = min(DMXvalue, 255)
            print("######  Recieved message: channel: "+str(DMXchannel)+" value: "+str(DMXvalue))
            #self.shout("ZOCP", json.dumps({ 'MOD' :self.capability}).encode('utf-8'))

            self.dp.set(int(DMXchannel), int(DMXvalue))
            self.dp.send()

            # FERDY ..
            #print("@@@@@@@@@@ ")
            #print(self.capability)
            #key = self.capability['key']['value']

            #if(key == 'k'):
            #    self.dp.set(340,0)  # set DMX channel 
            #    self.dp.set(342,0)  # set DMX channel 
            #    self.dp.set(345,255)  # set DMX channel 
            #    self.dp.set(346,255)  # set DMX channel 
            #    self.dp.set(347,255)  # set DMX channel 
            #    self.dp.send()
            #    print(" -->>> GOT FERDY")   


            
        else:
            print("not running...")


if __name__ == '__main__':
    #z = ZOCP()
    z = Artnetnode("ZOCP-Artnet-Receive")
    z.register_int('DMXchannel', 10, access='rw', min=0, max=999, step=1)
    z.register_int('DMXvalue', 10, access='rw', min=0, max=255, step=1)
    
    z.run()
    z.stop()
    print("FINISH")


    

          
          


