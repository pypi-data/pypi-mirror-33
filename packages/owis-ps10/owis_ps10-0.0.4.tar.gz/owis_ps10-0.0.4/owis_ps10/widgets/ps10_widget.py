# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 08:40:20 2015

@author: twagner
"""

### imports ###################################################################
import logging
import numpy as np
import os
import yaml

#### imports from #############################################################
from PyQt5.QtCore import pyqtSignal, QSize, QTimer
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction, QGridLayout, QGroupBox, QHBoxLayout
from PyQt5.QtWidgets import QLabel, QLineEdit, QMessageBox
from PyQt5.QtWidgets import QToolButton, QVBoxLayout, QWidget
from PyQt5.QtGui import QDoubleValidator, QIcon, QKeySequence

### relative imports ##########################################################
from .warnings import warnChangeWafer, warnMoveToSampleChangePosition
from .warnings import warnNoVacuum, warnWaferNotSuckedIn
import myowis.owis_timer as owis_timer

### logger ####################################################################
logging.getLogger('owis_widget').addHandler(logging.NullHandler())

###############################################################################
class PS10Widget(QWidget):
    """
    Widget for hardware controls.
    """
    ### signals
    gotoRef = pyqtSignal()
    gotoScan = pyqtSignal()
    sig_ref = pyqtSignal()

    def __init__(self, hardware, configFilename):
        super(PS10Widget, self).__init__()

        self.logger = logging.getLogger('owis_widget')        

        self._scanPosition = 0.
        self.scanPositionSave = 0.

        self.scanPositions = {}
        self.maxPositions = {}
        self.flatOffsets = {}

        # filepath = os.path.dirname(os.path.abspath(__file__))
        filepath = os.getcwd()
        
        fullfile = os.path.join(filepath, configFilename)
        
        with open(fullfile) as data_file:    
            data = yaml.load(data_file)

        lrtData = data['widget']['LRT']
        self.upDist = lrtData['upMove']
        self.upFastDist = lrtData['upMoveFast']
        self.downDist = lrtData['downMove']
        self.downFastDist = lrtData['downMoveFast']

        drtData = data['widget']['DRT']
        self.leftDist = drtData['leftMove']
        self.leftFastDist = data['widget']['DRT']['leftMoveFast']
        self.rightDist = data['widget']['DRT']['rightMove']
        self.rightFastDist = data['widget']['DRT']['rightMoveFast']

        self.iconPath = data['widget']['icons']

        self.msgRef = data['widget']['msgRef']
        
        self.hardware = hardware
        self.hardware.digitalOutput[0].verbosity = 1
        self.hardware.needReference = data['hardware']['needReference']
        self.hardware.needVacuum = data['hardware']['needVacuum']
        self.hardware.offsetMark = data['hardware']['offsetMark']

        positions = data['positions']
        
        for position in positions:
            name = position['name']
            self.scanPositions[name] = position['LRT']
            self.maxPositions[name] = position['LRTmax']
            self.flatOffsets[name] = position['LRTflat']
            
        self.mountPlateType = 'Wafer6'
        self.scanPositionSave = self.scanPositions[self.mountPlateType]
        
        self.initUI()
        self.initEvents()
        
    def initUI(self):
        self.txtPos = QLabel('(%5.1f mm, %5.1f deg.)' % (0.0, 0.0))
        self.txtPos.setMinimumWidth(110)
        self.posTimer = QTimer()

        self.txtMoveR = QLineEdit()
        self.txtMoveTheta = QLineEdit()
        
        buttonSize = QSize(105, 105)
        controlButtonSize = QSize(80, 80)
        iconSize = QSize(46, 46)
        
        owisPath = os.path.dirname(os.path.abspath(__file__))
        iconPath = os.path.join(owisPath, 'icons')
        iconPath = "\\\\fcmfs1\\DATA\\MESSTECH\\FCM_Software\\Icons"
        iconPath = self.iconPath

        # icons http://www.flaticon.com/

        buttons = {
            'Ref': ('&Referenzfahrt', "home-button.png", buttonSize),

            'Down': (
                self.tr('%+0.1f cm' % (self.downDist / 2.0)),
                "down-arrow-of-angle.png",
                controlButtonSize
            ),
                     
            'FastDown': (
                self.tr('%+0.1f cm' % (self.downFastDist / 2.0)),
                "two-down-arrows.png",
                controlButtonSize
            ),
                         
            'FastUp': (
                self.tr('%+0.1f cm' % (self.upFastDist / 2.0)),
                "two-arrows-pointing-up.png",
                controlButtonSize
            ),

            'FastLeft': (
                self.tr(u'%+0.1f°' % self.leftFastDist),
                "rewind-double-arrows-angles.png",
                controlButtonSize
            ),
                         
            'FastRight': (
                self.tr(u'%+0.1f°' % self.rightFastDist),
                "fast-forward-double-right-arrows.png",
                controlButtonSize
            ),
                         
            'Left': (
                self.tr(u'%+0.1f°' % self.leftDist),
                "left-arrow-angle.png",
                controlButtonSize
            ),

            'Right': (
                self.tr(u'%+0.1f°' % self.rightDist),
                "right-arrow-angle.png",
                controlButtonSize
            ),

            'Stop': (
                self.tr('Sto&pp'),
                "cancel-button.png",
                buttonSize
            ),

            'Turn': (
                self.tr(u'180°'),
                "up-curved-arrow.png",
                controlButtonSize
            ),

            'Up': (
                self.tr('%+0.1f cm' % (self.upDist / 2.0)),
                "up-arrow-angle.png",
                controlButtonSize
            ),
        }
        
        for key, btnParams in buttons.items():
            btnText, iconFilename, btnSize = btnParams

            btnName = 'btn' + key
            button = QToolButton()
            button.setMinimumSize(btnSize)
            button.setText(btnText)

            icon = QIcon(os.path.join(iconPath, iconFilename))
            button.setIcon(icon)
            button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            button.setIconSize(iconSize)

            setattr(self, btnName, button)
            
        icons = {
            'vacuumIcon': "vacuum-tip.png"
        }

        for key, filename in icons.items():
            icon = QIcon(os.path.join(iconPath, filename))
            setattr(self, key,  icon)

        
        self.txtMoveR.setMaxLength(5)
        self.txtMoveR.setValidator(QDoubleValidator())
        
        self.txtMoveTheta.setMaxLength(5)
        self.txtMoveTheta.setValidator(QDoubleValidator())

        self.lightCurtain = owis_timer.LightCurtain(
            self.hardware, iconSize, buttonSize
        )
        
        self.lightCurtain.vacButton.setIcon(self.vacuumIcon)
        self.lightCurtain.btnRef = self.btnRef
        self.lightCurtain.sig_ref = self.sig_ref
        self.lightCurtain.initDRTPosition = self.hardware.offsetMark
        
        lrtBox = QGroupBox("Lineartisch")
        lrtLayout = QGridLayout()
        lrtLayout.addWidget(self.btnUp, 0, 0)
        lrtLayout.addWidget(self.btnDown, 1 ,0)
        lrtLayout.addWidget(self.btnFastUp, 0, 1)
        lrtLayout.addWidget(self.btnFastDown, 1, 1)
        lrtBox.setLayout(lrtLayout)
        lrtBox.setFixedWidth(190)

        drtBox = QGroupBox("Drehtisch")
        drtLayout = QGridLayout()
        drtLayout.addWidget(self.btnLeft, 0, 0, 2, 2)
        drtLayout.addWidget(self.btnFastLeft, 2, 0, 2, 2)
        drtLayout.addWidget(self.btnTurn, 4, 1, 2, 2)
        drtLayout.addWidget(self.btnRight, 0, 2, 2, 2)
        drtLayout.addWidget(self.btnFastRight, 2, 2, 2, 2)
        drtBox.setLayout(drtLayout)
        drtBox.setFixedWidth(190)

        controlBox = QGroupBox("Owis")
        controlLayout = QGridLayout()
        controlLayout.addWidget(self.btnRef, 2, 0, Qt.AlignCenter)
        controlLayout.addWidget(
            self.lightCurtain.vacButton, 0, 0, Qt.AlignCenter
        )
        controlLayout.addWidget(self.btnStop, 3, 0, Qt.AlignCenter)
        controlLayout.addWidget(self.txtPos, 4, 0, Qt.AlignCenter)
        controlBox.setLayout(controlLayout)

        tableLayout = QVBoxLayout()
        tableLayout.addWidget(lrtBox)
        tableLayout.addWidget(drtBox)
        tableLayout.addStretch()

        owisLayout = QVBoxLayout()
        owisLayout.addWidget(controlBox)
        owisLayout.addStretch()
        
        layout = QHBoxLayout()
        layout.addLayout(tableLayout)
        layout.addLayout(owisLayout)
        layout.addStretch()
        self.setLayout(layout)
        
    def initEvents(self):
        self.btnRef.clicked.connect(self.goReference)
        self.btnUp.clicked.connect(self.doUp)
        self.btnDown.clicked.connect(self.doDown)
        self.btnFastUp.clicked.connect(self.doUpFast)
        self.btnFastDown.clicked.connect(self.doDownFast)
        self.btnLeft.clicked.connect(self.doLeft)
        self.btnFastLeft.clicked.connect(self.doLeftFast)
        self.btnRight.clicked.connect(self.doRight)
        self.btnFastRight.clicked.connect(self.doRightFast)
        self.btnTurn.clicked.connect(self.doTurn)
        self.btnStop.clicked.connect(self.doStop)
        self.txtMoveR.returnPressed.connect(self.doMoveR)
        self.txtMoveTheta.returnPressed.connect(self.doMoveTheta)

        self.posTimer.timeout.connect(self.doUpdatePosition)
        self.posTimer.start(1000)

        actionList = [
            ["go to reference", "Ctrl+R", self.goReference],
            [
                "stop",
                QKeySequence(Qt.Key_Escape),
                self.btnStop.click
            ],    
            ["up", QKeySequence(Qt.Key_Up), self.doUp],
            ["down", QKeySequence(Qt.Key_Down), self.doDown],
            ["left", QKeySequence(Qt.Key_Left), self.doLeft],
            ["right", QKeySequence(Qt.Key_Right), self.doRight],
            ["shiftUp", "Shift+Up", self.doUpFast],
            ["shiftDown", "Shift+Down", self.doDownFast],
            ["shiftLeft", "Shift+Left", self.doLeftFast],
            ["shiftRight", "Shift+Right", self.doRightFast],
            ["turn", "PgDown", self.doTurn],
        ]

        for a in actionList:
            action = QAction(
                a[0],
                self,
                shortcut = QKeySequence(a[1]),
                triggered = a[2])
        
            self.addAction(action)

        
    ### properties
    @property
    def scanPosition(self):
        return self._scanPosition
        
    @scanPosition.setter
    def scanPosition(self, value):
        self._scanPosition = value

    ### methods
    def checkForReference(self, axis):
        if(not self.hardware.checkReference(axis)):
            msgRef = QMessageBox()

            message = (
                u"Keine Referenzposition gefunden. " +
                u"Jetzt eine Referenzfahrt durchführen?"
            )

            msgRef.setText(message)

            msgRef.setStandardButtons(
                QMessageBox.Ok | QMessageBox.Cancel
            )

            ret = msgRef.exec_()
            
            if(ret == QMessageBox.Ok):
                self.goReference()


    def checkForVacuum(self):
        hasVac = self.lightCurtain.vacuum
        
        if(not hasVac and self.hardware.needVacuum):
            warnNoVacuum()
        
        return hasVac


    def checkForSuckedIn(self):
        hasVac = self.checkForVacuum()
        isSuckedIn = self.lightCurtain.suckedIn

        if hasVac:
            if(not isSuckedIn and self.hardware.needVacuum):
                warnWaferNotSuckedIn()
        
        return isSuckedIn


    def goReference(self, warning = True):
        if warning:
            if not self.lightCurtain.vacuum:
                QMessageBox.warning(self, "Referenzfahrt", self.msgRef)

        self.logger.info('moving to reference position ...')
        
        self.hardware.moveRef()
        # self.hardware.moveRefOrg()

        self.lightCurtain.initDRTPosition = self.hardware.reference.drt
        self.sig_ref.emit()


    def goScan(self, position, angle = None):
        self.checkForReference(self.hardware.AXIS_LRT)

        ### move linear        
        self.hardware.moveAbsolute(
            self.hardware.AXIS_LRT,
            position
        )
        
        ### Python3 has no long() method, use int() instead
        try:
            long(0)
        except NameError:
            long = int
        
        ### rotate
        if (
            isinstance(angle, (int, long, float)) and
            not isinstance(angle, bool)
        ):
            self.checkForSuckedIn()
            self.hardware.moveAbsolute(self.hardware.AXIS_DRT, angle)

        self.scanPosition = position

    def doUpdatePosition(self):
        l = self.hardware.getPosition(1)
        alpha = self.hardware.getPosition(2)

        # print('doUpdatePosition')
        
        self.txtPos.setText('(%5.1f mm, %5.1f deg.)' % (l, alpha))


    def doUp(self):
        self.checkForReference(self.hardware.AXIS_LRT)
        self.hardware.moveRelative(self.hardware.AXIS_LRT, self.upDist)


    def doDown(self):
        self.checkForReference(self.hardware.AXIS_LRT)
        self.hardware.moveRelative(self.hardware.AXIS_LRT, self.downDist)


    def doUpFast(self):
        self.checkForReference(self.hardware.AXIS_LRT)
        self.hardware.moveRelative(self.hardware.AXIS_LRT, self.upFastDist)


    def doDownFast(self):
        self.checkForReference(self.hardware.AXIS_LRT)
        self.hardware.moveRelative(self.hardware.AXIS_LRT, self.downFastDist)


    def doLeft(self):
        self.checkForReference(self.hardware.AXIS_DRT)
        self.checkForSuckedIn()
        self.hardware.moveRelative(self.hardware.AXIS_DRT, self.leftDist)

    def doLeftFast(self):
        self.checkForReference(self.hardware.AXIS_DRT)
        self.checkForSuckedIn()
        self.hardware.moveRelative(self.hardware.AXIS_DRT, self.leftFastDist)


    def doRight(self):
        self.checkForReference(self.hardware.AXIS_DRT)
        self.checkForSuckedIn()
        self.hardware.moveRelative(self.hardware.AXIS_DRT, self.rightDist)


    def doRightFast(self):
        self.checkForReference(self.hardware.AXIS_DRT)
        self.checkForSuckedIn()
        self.hardware.moveRelative(self.hardware.AXIS_DRT, self.rightFastDist)


    def doTurn(self):
        self.checkForReference(self.hardware.AXIS_DRT)
        self.checkForSuckedIn()
        self.hardware.moveRelative(self.hardware.AXIS_DRT, 180)

        self.hardware.getCurrentPosition()
        
    def doStop(self):
        self.hardware.axisLRT.stop()
        self.hardware.axisDRT.stop()


    def doMoveR(self):
        self.logger.info("moving relative: %s", self.txtMoveR.text())
        self.hardware.moveRelative(1, float(self.txtMoveR.text()))


    def doMoveTheta(self):
        self.logger.info("Move Theta: %", self.txtMoveTheta.text())
        self.hardware.moveRelative(2, float(self.txtMoveTheta.text()))

    def doDiameter(self, diameter):
        self.logger.info("received diameter: %s", diameter)

        if diameter == '76,2':
            plate = 'Wafer3'
        elif diameter == '100':
            plate = 'Wafer4'
        elif diameter == '150':
            plate = 'Wafer6'
        elif diameter == '200':
            plate = 'Wafer8'
        else:
            self.logger.error("wafer diameter not recognized: %s", diameter)
            plate = 'Wafer6'

        lrt, drt = self.hardware.getCurrentPosition()
            
        pos = self.scanPositions[plate]

        if (np.abs(lrt - pos) > 10.0 and lrt > 0.):
            if warnMoveToSampleChangePosition():
                self.logger.info("going to reference position ...")
                self.goReference(warning = False)
                self.logger.info("reference position reached")
    
                warnChangeWafer(diameter)
    
                self.logger.info("plate for %s mm wafer mounted", diameter)
                

    def restoreScanPosition(self):
        self.scanPosition = self.scanPositionSave
