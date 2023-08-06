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
class Axis(QWidget):
    def __init__(self, axis):
        super(Axis, self).__init__()

        self.axis = axis
        
        self.initUI()
        self.initTimer()
        self.initEvents()
        
    def initUI(self):
        self.errorState = QPushButton()
        self.errorState.setCheckable(True)

        layout = QHBoxLayout()
        layout.addWidget(self.errorState)
        
        self.setLayout(layout)

    def initTimer(self):
        self.timer = QTimer()

        self.timer.start(1000)

    def initEvents(self):
        self.timer.timeout.connect(self.doUpdate)

    def doUpdate(self):
        errorState = self.axis.errorState
        position = self.axis.position
        
        if errorState == 0:
            self.errorState.setChecked(True)
        elif errorState == 4:
            self.errorState.setChecked(False)

        self.errorState.setText(str(position))
