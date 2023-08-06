# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 08:40:20 2015

@author: twagner
"""

### imports ###################################################################
import logging

#### imports from #############################################################
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QWidget
from PyQt5.QtCore import QTimer

### logger ####################################################################
logging.getLogger('owis_widget').addHandler(logging.NullHandler())

###############################################################################
class DigitalInput(QWidget):
    def __init__(self, hardware):
        super(DigitalInput, self).__init__()

        self.counter = 0
        self.hardware = hardware
        self.logger = logging.getLogger('owis_widget')        
        self.refreshRate = 1.

        self.initUI()
        self.initTimer()
        self.initEvents()
        
    def initUI(self):
        self.button = []
        layout = QHBoxLayout()
        
        for i in range(4):
            button = QPushButton(str(i))
            button.setCheckable(True)
            self.button.append(button)
            layout.addWidget(button)           

        self.setLayout(layout)

    def initEvents(self):
        self.timer.timeout.connect(self.doUpdate)

    def initTimer(self):
        self.timer = QTimer()
        self.logger.info("starting timer")

        refreshTime = 1000 / self.refreshRate
        self.timer.start(refreshTime)

    def doUpdate(self):
        digitalInput = self.hardware.digitalInput[0].value

        if digitalInput == 1:
            self.button[0].setChecked(True)
        else:
            self.button[0].setChecked(False)

    def stopTimer(self):
        self.logger.info("stoping timer")
        self.timer.stop()
