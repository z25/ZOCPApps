#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
zqtLCDdisplay.py
PySide Qt ZOCP LCD display example
"""


import sys
import zmq
import logging
import socket

from zocp import ZOCP
from PySide import QtGui, QtCore

class QTZOCPnumber(QtGui.QWidget):
    
    def __init__(self):
        super(QTZOCPnumber, self).__init__()

         # Set name of Node
        self.nodename = "QT LCDdisplay@%s" % socket.gethostname()

        self.init_zocp()
        self.initUI()

    def init_zocp(self):
        self.z = ZOCP()
        self.z.set_node_name(self.nodename)
        
        self.notifier = QtCore.QSocketNotifier(
                self.z.inbox.getsockopt(zmq.FD), 
                QtCore.QSocketNotifier.Read
                )
        self.notifier.setEnabled(True)
        self.notifier.activated.connect(self.zocp_event)
        self.z.on_peer_signaled = self.on_peer_signaled
        self.z.on_peer_enter = self.on_peer_enter
        self.z.start()

          
    def initUI(self):
        
        self.lcd1 = QtGui.QLCDNumber(self)
        self.lcd2 = QtGui.QLCDNumber(self)
        self.lcd3 = QtGui.QLCDNumber(self)

        # Register the ZOCP variables
        self.z.register_int("display1", 0, access='rs')
        self.z.register_int("display2", 0, access='rs')
        self.z.register_int("display3", 0, access='rs')

        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(self.lcd1, 1, 1)
        grid.addWidget(self.lcd2, 1, 2)
        grid.addWidget(self.lcd3, 1, 3)
        
        self.setLayout(grid) 
        self.setGeometry(300, 300, 150, 70)
        self.setWindowTitle(self.nodename)
        self.show()

        

    def zocp_event(self):
        self.z.run_once(0)

    def on_peer_signaled(self, peer, name, data, *args, **kwargs):
        """
        Called when a peer signals that some of its data is modified.

        peer: id of peer whose data has been changed
        name: name of peer whose data has been changed
        data: changed data, formatted as [emitter, value]
              emitter: name of the emitter on the subscribee
              value: value of the emitter
        """
        zl.debug(" --> ZOCP PEER SIGNALED: %s modified %s" %(name, data))

        # Check if there is data
        if(len(data) > 1):

            if(data[0] == "slider1"):
                self.lcd1.display(data[1])
            elif(data[0] == "slider2"):
                self.lcd2.display(data[1])
            elif(data[0] == "slider3"):
                self.lcd3.display(data[1])


    def on_peer_enter(self, peer, name, *args, **kwargs):
        
        zl.debug(" -----> PEER ENTERED ",name," peer: ",peer)
        # This assumes that for testing the source to connect to is running on the same computer as the 
        # the destination trying to connect to it is.
        sourceTargetName = "QT Sliders@%s" % socket.gethostname()
        if(name == sourceTargetName):
            self.z.signal_subscribe(self.z.uuid(), 'display1', peer, 'slider1')
            self.z.signal_subscribe(self.z.uuid(), 'display2', peer, 'slider2')
            self.z.signal_subscribe(self.z.uuid(), 'display3', peer, 'slider3')
            zl.debug("Nodes are subscribed")


    def closeEvent(self, *args):
        zl.debug(args)
        self.z.stop()



       
def main():
    app = QtGui.QApplication(sys.argv)
    window = QTZOCPnumber() 
    app.exec_()


if __name__ == '__main__':
    # Enalbel logging
    zl = logging.getLogger("zocp")
    zl.setLevel(logging.DEBUG)


    main()
