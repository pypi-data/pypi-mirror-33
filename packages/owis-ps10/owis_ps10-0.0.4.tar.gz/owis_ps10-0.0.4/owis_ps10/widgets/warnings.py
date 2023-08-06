# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 08:40:20 2015

@author: twagner
"""

### imports ###################################################################
import logging

#### imports from #############################################################
from PyQt5.QtWidgets import QMessageBox

### logger ####################################################################
logging.getLogger('owis_widget').addHandler(logging.NullHandler())

### global variable ###########################################################
warnStyle = "<span style = 'font-size: 14pt; font-weight: bold'>"

###############################################################################
def warnMoveToSampleChangePosition():
    message = (
        warnStyle + 
        u"Der Waferdurchmesser hat sich geändert." + "\n" +
        "Fahre zu Beladeposition."
    )

    title = "Beladeposition anfahren"

    msgBox = QMessageBox()

    yesButton = msgBox.addButton("Ja", QMessageBox.YesRole)
    noButton = msgBox.addButton("Nein", QMessageBox.NoRole)
    
    msgBox.setWindowTitle(title)
    msgBox.setText(message)
    msgBox.setDefaultButton(noButton)
    
    msgBox.exec_()

    result = (msgBox.clickedButton() == yesButton)

    return result

        
def warnNoVacuum():
    msgBox = QMessageBox()
    msgBox.setWindowTitle("Kein Vakuum")

    message = (u"Drehung ist ohne angelegtes Vakuum nicht möglich.")
    
    msgBox.setText(message)
    
    msgBox.exec_()
    

def warnChangeWafer(diameter):
    msgBox = QMessageBox()

    message = (
        warnStyle +
        u"Auflageplatte für " + diameter + " mm Wafer jetzt wechseln!"
    )

    msgBox.setText(message)
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.exec_()
    

def warnWaferNotSuckedIn():
    msgBox = QMessageBox()
    msgBox.setWindowTitle("Kein Vakuum")

    message = (
            u"""Der Wafer ist für eine Drehung nicht genügend angesaugt
                oder es liegt kein Wafer auf.""")
    
    msgBox.setText(message)
    
    msgBox.exec_()
