# -*- coding: utf-8 -*-
"""
Created on Thu Nov 05 13:47:34 2015

@author: twagner
"""

### imports ###################################################################
import logging
import os

### imports from ##############################################################
from PyQt5 import QtGui
from PyQt5 import QtWidgets

if os.name != "posix":
    from PyQt5 import QAxContainer

###############################################################################
logging.getLogger('mikrocad').addHandler(logging.NullHandler())

###############################################################################
class DummyWidget(QtWidgets.QWidget):
    def __init__(self):
        super(DummyWidget, self).__init__()
        
    def dynamicCall(self, handle):
        return 0

###############################################################################
class LiveWidget(QtWidgets.QWidget):
    def __init__(self):
        super(LiveWidget, self).__init__()

        self.logger = logging.getLogger('mikrocad')
        
        self.initUI()
        self.initEvents()
        
        self.handle = self.winformControl.dynamicCall("getHandle()")  

        if type(self.handle) == int:
            self.logger.debug('Live image widget handle: %i', self.handle)
        else:
            self.logger.debug("type of winform handle:", type(self.handle))
            self.handle = self.handle.toPyObject()
        
    def initUI(self):
        if os.name != "posix":
            self.winformControl = QAxContainer.QAxWidget(self)
            self.winformControl.setControl("Hello.UserControl")
        else:
            self.winformControl = DummyWidget()
    
        vbox = QtWidgets.QVBoxLayout(self)
        
        self.setLayout(vbox)

        vbox.addWidget(self.winformControl)
        self.setFixedSize(512, 512)
        
    def initEvents(self):
        action = QtWidgets.QAction(
            "Action",
            self,
            shortcut = QtGui.QKeySequence("P, S"),
            triggered = self.doScreenShot)
    
        self.addAction(action)

    def doScreenShot(self):
        filename = __file__.replace('.py', '.png')
        print("Saving GUI screenshot to", filename, "...")
        p = QtGui.QPixmap.grabWindow(self.winId())
        p.save(filename, 'png')
        print("Done.")

    
    


