# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 08:40:20 2015

@author: twagner
"""

### imports ###################################################################
import logging

#### imports from #############################################################
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QWidget

### logger ####################################################################
logging.getLogger('owis_widget').addHandler(logging.NullHandler())

###############################################################################
class MountPlate(QWidget):
    def __init__(self, hardware):
        super(MountPlate, self).__init__()

        self.hardware = hardware
        self.mountPlate = None
        self.wafer = None

        self.initUI()
        self.initEvents()
        
    def initUI(self):
        self.mountPlateButton = QPushButton('mount plate')
        self.mountPlateButton.setCheckable(True)

        self.waferButton = QPushButton('wafer')
        self.waferButton.setCheckable(True)

        self.lightCurtainButton = QPushButton('light curtain')
        self.lightCurtainButton.setCheckable(True)

        layout = QHBoxLayout()
        layout.addWidget(self.mountPlateButton)
        layout.addWidget(self.waferButton)
        layout.addWidget(self.lightCurtainButton)

        self.setLayout(layout)
        
    def initEvents(self):
        self.mountPlateButton.clicked.connect(self.doSwitchMountPlate)
        self.waferButton.clicked.connect(self.doSwitchWafer)
        self.lightCurtainButton.clicked.connect(self.doLightCurtain)


    def doLightCurtain(self):
        if self.lightCurtainButton.isChecked():
            self.hardware.axisLRT.errorState = 4
            self.hardware.axisDRT.errorState = 4
        else:
            self.hardware.axisLRT.errorState = 0
            self.hardware.axisDRT.errorState = 0
            
    def doSwitchMountPlate(self):
        if self.mountPlateButton.isChecked():
            self.hardware.digitalInput[0].value = 1
        else:
            self.hardware.digitalInput[0].value = 0

    def doSwitchOutput(self, pin):
        if pin == 1:
            checked = self.waferButton.isChecked()
            output = self.hardware.digitalOutput[0].value

            if checked:
                if output == 1:
                    self.hardware.digitalInput[0].value = 1
                else:
                    self.hardware.digitalInput[0].value = 0

    def doSwitchWafer(self):
        checked = self.waferButton.isChecked()

        if checked:
            if self.hardware.digitalOutput[0].value == 1:
                self.hardware.digitalInput[0].value = 1
            else:
                self.hardware.digitalInput[0].value = 0
        else:
            if self.hardware.digitalOutput[0].value == 1:
                self.waferButton.setChecked(True)
                self.hardware.digitalInput[0].value = 1
            else:
                self.hardware.digitalInput[0].value = 0
