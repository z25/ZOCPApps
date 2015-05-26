#!/usr/bin/env python3
#-*- coding: utf-8 -*-
"""
zqt_ui_node.py
PySide Qt ZOCP Sliders Node example
"""

import sys
import zmq
import logging
import socket

from zocp import ZOCP
from PySide import QtCore, QtGui

class QTZOCPNode(QtGui.QWidget):

    def __init__(self):
        super(QTZOCPNode, self).__init__()

        # Set name of Node
        self.nodename = "QT Sliders@%s" % socket.gethostname()
        
        self.init_zocp()
        self.initUI()
 
    def init_zocp(self):
        self.z = ZOCP(self.nodename)
        
        self.notifier = QtCore.QSocketNotifier(
                self.z.inbox.getsockopt(zmq.FD), 
                QtCore.QSocketNotifier.Read
                )
        self.notifier.setEnabled(True)
        self.notifier.activated.connect(self.zocp_event)
        self.z.start()

    def initUI(self):      

        # Create Sliders
        sld1 = self.createSlider("slider1",0,100)
        sld2 = self.createSlider("slider2",0,100)
        sld3 = self.createSlider("slider3",0,100)

        # Create Layout Grid
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        # add all the widgets to the grid
        grid.addWidget(sld1, 1, 1)
        grid.addWidget(sld1.label, 2, 1)
        grid.addWidget(sld2, 1, 2)
        grid.addWidget(sld2.label, 2, 2)
        grid.addWidget(sld3, 1, 3)
        grid.addWidget(sld3.label, 2, 3)
        
        # set layout of window
        self.setLayout(grid) 
        self.setGeometry(300, 300, 280, 170)
        self.setWindowTitle(self.nodename)
        self.show()

    def createSlider(self, _id, _min, _max):

        sld = QtGui.QSlider(QtCore.Qt.Vertical, self)
        sld.setAccessibleName(_id)
        sld.setFocusPolicy(QtCore.Qt.NoFocus)
        sld.valueChanged[int].connect(self.changeValue)
        sld.setMinimum(_min)
        sld.setMaximum(_max)
        
        sld.label = QtGui.QLabel(self)
        sld.label.setText(_id)

        # Register the ZOCP variable
        self.z.register_float(_id, 0, access='rwe', min=_min, max=_max, step=1)

        return sld

    def changeValue(self, value):
        sender = self.sender().accessibleName()
        zl.debug("value ",value," id ",sender)

        # ZOCP: HANDLE VALUE CHANGE  
        self.z.emit_signal(sender, value)

    
    # HANDLE INCOMING ZOCP MESSAGES 
    def zocp_event(self):
        self.z.run_once(0)
         
    def closeEvent(self, *args):
        zl.debug(args)
        self.z.stop()


def main():
    app = QtGui.QApplication(sys.argv)
    window = QTZOCPNode() 
    app.exec_()


if __name__ == '__main__':
    # Enable Logging
    zl = logging.getLogger("zocp")
    zl.setLevel(logging.DEBUG)

    main()
