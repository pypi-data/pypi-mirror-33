# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 08:30:13 2016

@author: twagner
"""

### imports ###################################################################
import logging
import qtpy
import qtpy.QtGui as QtGui

if qtpy.PYQT4:
    import PyQt4.QtCore as QtCore
elif qtpy.PYQT5:
    import PyQt5.QtCore as QtCore
else:    
    import qtpy.QtCore as QtCore
    
import qtpy.QtWidgets as QtWidgets

###############################################################################
from qtpy.QtCore import QTimer

# from PyQt4.QtCore import SIGNAL 

# from eval_aux import timestamp

logging.getLogger('owis_timer').addHandler(logging.NullHandler())

###############################################################################
class LightCurtain(QtWidgets.QWidget):
    """
    Originally the light curtain watcher.
    Now performing all background checks of controller state changes.
    Controls vacuum as well.
    """

    sig_ref = QtCore.pyqtSignal()

    def __init__(
        self, hardware = None, iconSize = QtCore.QSize(54, 54),
        buttonSize = QtCore.QSize(110,110)
    ):
        super(LightCurtain, self).__init__()

        self.logger = logging.getLogger('owis_timer')

        self.refreshRate = 10 # 1/s

        self.offMsg = self.tr(
                'Zur Entnahmeposition \n fahren \n &Vakuum ausschalten')
        
        self.onMsg = self.tr('&Vakuum einschalten')

        self.hardware = hardware
        self.hardware.digitalInput[0].verbosity = 1
        self.hardware.digitalOutput[0].verbosity = 1

        self.initDRTPosition = self.hardware.reference.drt

        self.waitForVacuum = False
        self.waitForReference = False

        self.oldReferenceState = -1

        self.iconSize = iconSize
        self.buttonSize = buttonSize

        # dummy until we get the real button from super class
        self.btnRef = QtWidgets.QToolButton()

        self._suckedIn = False
        self._vacuum = False

        self.initUI()
        self.initTimer()
        self.initEvents()

        
    def initUI(self):
        
        self.vacButton = QtWidgets.QToolButton()
        self.vacButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.vacButton.setText(self.onMsg)
        self.vacButton.setIcon(QtGui.QIcon('icons/vacuum-tip.png'))
        self.vacButton.setIconSize(self.iconSize)
        self.vacButton.setMinimumSize(self.buttonSize)
        
        if self.vacuum:
            self.vacuum = True
        else:
            self.vacuum = False

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.vacButton)

        self.setLayout(layout)


    def initEvents(self):
        self.timer.timeout.connect(self.update)
        # self.connect(self.timer, SIGNAL("timeout()"), self.update)
        self.vacButton.clicked.connect(self.doSwitchVac)


    def initTimer(self):
        self.timer = QTimer()
        self.logger.info("Starting timer")
        refreshTime = 1000 / self.refreshRate
        self.timer.start(refreshTime)

    #%%
    @property
    def suckedIn(self):
        if self.hardware.vacuumInput.value == 1:
            self._suckedIn = True
        else:
            self._suckedIn = False
            
        return self._suckedIn
    
    @suckedIn.setter
    def suckedIn(self, value):
        pass
        
    #%%
    @property
    def vacuum(self):
        if self.hardware.vacuumOutput.value == 1:
            self._vacuum = True
        else:
            self._vacuum = False
            
        return self._vacuum

    @vacuum.setter
    def vacuum(self, value):
        if value:
            self.hardware.vacuumOutput.value =  1

            self.initDRTPosition = self.hardware.getPosition(
                self.hardware.AXIS_DRT
            )
            
            self.vacButton.setText(self.offMsg)
    
            self.logger.info(
                "Switch on vacuum, current DRT position: %d)",
                self.initDRTPosition
            )
        else:
            self.hardware.vacuumOutput.value = 0
            self.vacButton.setStyleSheet('background-color: none')
            self.vacButton.setText(self.onMsg)
            self.logger.info("Switch off vacuum")
            
    ### methods
    def doSwitchVac(self):
        if self.vacuum == False:
            self.vacuum = True

        else:
            pos = self.hardware.getPosition(self.hardware.AXIS_DRT)

            if(pos != self.initDRTPosition):
                self.logger.info("DRT is rotated. moving back: %s", pos)

                self.hardware.moveAbsolute(
                    self.hardware.AXIS_DRT, self.initDRTPosition
                )

                self.waitForVacuum = True

            else:
                self.vacuum = False

    #### timer control
    def stop(self):
        self.logger.info("Stoping timer")
        self.timer.stop()


    def update(self):
        # %% reference control
        self.hardware.checkReference(self.hardware.AXIS_DRT)
        self.hardware.checkReference(self.hardware.AXIS_LRT)
        
        if self.oldReferenceState != self.hardware.referenceState:
            self.sig_ref.emit()
            
            if self.hardware.maxReferenceState != 3:
                self.btnRef.setStyleSheet('background-color: red')
            else:
                self.btnRef.setStyleSheet('background-color: none')

            self.oldReferenceState = self.hardware.referenceState

        # %% vacuum control
        pos = self.hardware.getPosition(self.hardware.AXIS_DRT)
        
        if (self.waitForVacuum and pos == self.initDRTPosition):
            self.vacuum = False
            self.waitForVacuum = False

        if self.vacuum:
            if self.suckedIn == True:
                self.vacButton.setStyleSheet('background-color: green')
            else:
                self.vacButton.setStyleSheet('background-color: orange')
        else:
            self.vacButton.setStyleSheet('background-color: none')

        # watch emergency stop
        emergency = self.hardware.emergency
        
        if self.hardware.emergencyReleased:        
            self.hardware.axisLRT.motorInit()
            self.hardware.axisDRT.motorInit()

# %% main() ###################################################################    
if __name__ == "__main__":
    from owis import PS10

    # %% setup logger
    logging.basicConfig(
        format = '%(asctime)s %(name)11s %(levelname)7s %(message)s',
        level = logging.DEBUG,
        datefmt = '%Y-%m-%d %H:%M:%S'
    )

    console = logging.StreamHandler()
    fileHandler = logging.FileHandler('..\\log\\owis_timer.log', 'w')    
    
    logger = logging.getLogger("owis_timer")
    logger.addHandler(fileHandler)

    # %% init Qt application
    app = QtWidgets.QApplication([])
    
    # %% init OWIS controller
    ps10 = PS10('..\\config\\company_owis.cfg')
    
    # %% light curtain / vacuum control widget    
    lightCurtain = LightCurtain(ps10)
    lightCurtain.show()
    
    # %% start QtWidget
    app.exec_()
