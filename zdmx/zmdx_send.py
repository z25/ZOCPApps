#!/usr/bin/python

import json
import sys
#sys.path.append("../src/")
#sys.path.append("../../")
#print(sys.path)

from zocp import ZOCP



class DMXnode(ZOCP):

    dmx_recieve_node_id = None

    def __init__(self, *args, **kwargs):
        super(DMXNode, self).__init__(*args, **kwargs)

    def send_dmx_channel(self, channel, value):
        
        data = { "DMXchannel": {'value': channel},"DMXvalue": {'value': value}}
        stuur = json.dumps({'SET': data}).encode('utf-8')
        print(stuur,type(stuur))
        if(self.dmx_recieve_node_id != None):
            self.whisper(self.dmx_recieve_node_id, stuur)
            print(" SETTING DMX DATA to: ",self.dmx_recieve_node_id);

    

    def send_dmx_channels(self, channels, values):
        
        print(" ### START SETING CHANNELS ##########",len(channels),"################")
        i=0

        for channel in channels:
            data = { "DMXchannel": {'value': channel},"DMXvalue": {'value': values[i]}}
            stuur = json.dumps({'SET': data}).encode('utf-8')
            print(i,stuur,type(stuur))
            
            if(self.dmx_recieve_node_id != None):
                self.whisper(self.dmx_recieve_node_id, stuur)
            
            i+=1
            
        print(" ### DONE SETING CHANNELS ##########################")
            

    def on_peer_modified(self, peer, *args, **kwargs):
        #print("ZOCP ENTER   : %s" %(peer.hex))
        #print(peer)
        #print("##########################")
        
        if(self.dmx_recieve_node_id == None and args[0].get('_name') == "ZOCP-DMX-Recieve"):
            self.dmx_recieve_node_id = peer
            print("---> We found DMX recieve node numargs: ",numArgs)
            if numArgs == 3:
                z.send_dmx_channel(startChannel,value)
                #self.stop();
            if numArgs == 4:
                z.send_dmx_channels(channels,values)
                #self.stop();


    def on_peer_exit(self, peer, *args, **kwargs):
        if(peer == self.node_id):
            self.dmx_recieve_node_id = None
            print("---> We lost DMX recieve node")


    
        

if __name__ == '__main__':
    
    # cmdline arguments parse
    args = sys.argv
    print("##########################################################")
    print(args)
    print("##########################################################")

    '''
        first argument: start channel
        second argument: stop channel
        third argument: value
    '''

    z = DMXnode("ZOCP-DMX-send")

    numArgs = len(sys.argv)

    
    if numArgs == 4:

        startChannel = int(sys.argv[1])
        endChannel = int(sys.argv[2])
        value = int(sys.argv[3])

        channels = []
        values =[]
        for c in range(startChannel,endChannel+1):
            channels.append(c)
            values.append(value)

        print(channels)

        #z.send_dmx_channels(startChannel,value)


    if numArgs == 3:

        startChannel = int(sys.argv[1])
        value = int(sys.argv[2])
        #z.send_dmx_channel(startChannel,value)
 
 
    z.run()
    z.stop()
    print("FINISH")





