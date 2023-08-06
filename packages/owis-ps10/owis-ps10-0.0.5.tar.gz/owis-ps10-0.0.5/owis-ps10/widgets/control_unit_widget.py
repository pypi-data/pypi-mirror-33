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
class ControlUnit(QWidget):
    def __init__(self, hardware):
        super(ControlUnit, self).__init__()

        self.logger = logging.getLogger('owis_widget')        

        self.hardware = hardware

        self.refreshRate = 1
        
        self.initUI()
        self.initTimer()
        self.initEvents()

    def initEvents(self):
        self.timer.timeout.connect(self.doUpdate)

    def initUI(self):
        self.button = QPushButton()        
        self.button.setCheckable(True)

        layout = QHBoxLayout()
        layout.addWidget(self.button)
        
        self.setLayout(layout)

    def initTimer(self):
        self.timer = QTimer()
        self.logger.info("starting timer")

        refreshTime = 1000 / self.refreshRate
        self.timer.start(refreshTime)

    def doUpdate(self):
        emergency = self.hardware.emergency
        
        if emergency:
            self.button.setChecked(True)
        else:
            self.button.setChecked(False)