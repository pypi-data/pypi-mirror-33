# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 08:40:20 2015

@author: twagner
"""

### imports ###################################################################
import logging

#### imports from #############################################################
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QWidget
from PyQt5.QtCore import pyqtSignal

### logger ####################################################################
logging.getLogger('owis_widget').addHandler(logging.NullHandler())

###############################################################################
class DigitalOutput(QWidget):
    sigDigitalOutput = pyqtSignal(int)    

    def __init__(self, hardware):
        super(DigitalOutput, self).__init__()

        self.logger = logging.getLogger('owis_widget')        

        self.hardware = hardware

        self.initUI()
        self.initEvents()
        self.initOutputStates()


    def initOutputStates(self):
        for i in range(5):
            state = self.hardware.digitalOutput[i].value
            
            if state == 0:
                self.button[i].setChecked(False)
            elif state == 1:
                self.button[i].setChecked(True)
        
        
    def initUI(self):
        self.button = []
        layout = QHBoxLayout()
        
        for i in range(5):
            button = QPushButton(str(i))
            button.setCheckable(True)
            self.button.append(button)
            layout.addWidget(button)           

        self.verbosityButton = QPushButton()
        self.verbosityButton.setCheckable(True)

        self.setLayout(layout)


    def initEvents(self):
        for i in range(5):
            self.button[i].clicked.connect(self.doSwitchOutput)        

        self.verbosityButton.clicked.connect(self.doSwitchVerbosity)


    def doSwitchOutput(self):
        button = self.sender()
        iButton = int(button.text())
        pin = iButton + 1

        if button.isChecked():
            state = 1
        else:
            state = 0

        self.logger.info('Switch output pin %i to %i', pin, state)
        self.hardware.digitalOutput[iButton].value = state

        self.logger.info('Emitting digital output pin %i', pin)
        self.sigDigitalOutput.emit(pin)


    def doSwitchVerbosity(self):
        button = self.sender()
        
        if button.isChecked():
            self.hardware.digitalOutput[0].verbosity = 2
        else:
            self.hardware.digitalOutput[0].verbosity = 1
