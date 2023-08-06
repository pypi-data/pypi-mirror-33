# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 08:40:20 2015

@author: twagner
"""

### imports ###################################################################
import logging

#### imports from #############################################################
from pyqtgraph.dockarea import Dock, DockArea
from pyqtgraph.Qt import QtGui

### local imports #############################################################
from .digital_input import DigitalInput

### logger ####################################################################
logging.getLogger('owis_widget').addHandler(logging.NullHandler())

### global variable ###########################################################
warnStyle = "<span style = 'font-size: 14pt; font-weight: bold'>"

###############################################################################
class MainWindow(QtGui.QMainWindow):
    def __init__(self, hardware):
        super(MainWindow, self).__init__()

        self.hardware = hardware

        self.widgets = []

        self.initUI()
        self.initEvents()

    def initUI(self):
        self.axisLRT = Axis(self.hardware.axisLRT)
        self.axisDRT = Axis(self.hardware.axisDRT)
        self.digitalOutput = DigitalOutput(self.hardware)
        w2 = DigitalInput(self.hardware)
        self.mountPlate = MountPlate(self.hardware)
        self.controlUnit = ControlUnit(self.hardware)
        
        self.widgets = {
            'Axis LRT': self.axisLRT,
            'Axis DRT': self.axisDRT,
            'Digital Output': self.digitalOutput,
            'Digital Input': w2,
            'Mount Plate': self.mountPlate,
            'Control unit': self.controlUnit
        }

        area = DockArea()
        self.setCentralWidget(area)

        docks = []

        for name, widget in self.widgets.items():
            dock = Dock(name, autoOrientation = False)
            dock.addWidget(widget)
            area.addDock(dock)
            docks.append(dock)

        self.statusBar()
        
    def initEvents(self):
        self.digitalOutput.sigDigitalOutput.connect(
            self.mountPlate.doSwitchOutput
        )
