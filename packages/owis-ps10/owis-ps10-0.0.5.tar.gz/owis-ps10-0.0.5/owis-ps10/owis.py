# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 13:51:22 2015

@author: twagner
"""

### imports ###################################################################
import logging
import os
import serial.tools.list_ports
import threading
import time
import yaml

### imports from ##############################################################
from ctypes import c_char_p, c_double, c_int
from inspect import stack

if os.name != 'posix':
    from ctypes import WinDLL

### local imports #############################################################
# import owis_drt

#### logging ##################################################################
logging.getLogger('owis').addHandler(logging.NullHandler())

class Position:
    def __init__(self):
        self.lrt = 0.0
        self.drt = 0.0

###############################################################################
class AnalogInput(object):
    def __init__(self, dll, controller, pin):
        self.logger = logging.getLogger('owis')
        self.dll = dll
        self.controller = controller
        self.pin = pin
        self.verbosity = 1
        
        self._value = None

    @property
    def value(self):
        self._previousValue = self._value
        self._value = self.dll.PS10_GetAnalogInput(self.controller, self.pin)
        error = self.dll.PS10_GetReadError(self.controller)
        
        if error:
            self.logger.error(
                "Error getting analog input from pin %i: %i", self.pin, error
            )
            
        elif self.verbosity == 1:
            if self._value != self._previousValue:
                self.logger.debug(
                    "Analog input pin %i: %i", self.pin, self._value
                )
                
                self._previousValue = self._value

        elif self.verbosity == 2:
            self.logger.debug(
                "Analog input pin %i: %i", self.pin, self._value
            )
               
        return self._value


    @value.setter
    def value(self, value):
        self._value = value
        
        self.dll.analogInput[self.pin - 1] = value

###############################################################################
class Axis(object):
    def __init__(self, dll, controller, axis):
        self.logger = logging.getLogger('owis')
        
        self.axis = axis
        self.controller = controller
        self.dll = dll
        self.offsetMark = 0.       
        self.refMode = 4
        self._targetMode = 0
        self._targetEx = 0
        self.unit = '--'        

    ### properties ###
    #%%
    @property
    def accel(self):
        propertyName = stack()[0][3]
        return self.getProperty(propertyName)
        
    @accel.setter
    def accel(self, value):
        propertyName = stack()[0][3]
        self.setProperty(propertyName, value)

        
    #%%
    @property
    def conversion(self):
        propertyName = stack()[0][3]
        return self.getProperty(propertyName)
       
    @conversion.setter
    def conversion(self, value):
        propertyName = stack()[0][3]
        self.setProperty(propertyName, value)

        
    #%%
    @property
    def errorState(self):
        propertyName = stack()[0][3]
        return self.getProperty(propertyName)

    @errorState.setter
    def errorState(self, value):
        if hasattr(self.dll, 'errorState'):
            self.dll.errorState[self.axis - 1] = value        

    #%%
    @property
    def fastRefF(self):
        propertyName = stack()[0][3]
        return self.getProperty(propertyName)

    @fastRefF.setter
    def fastRefF(self, value):
        propertyName = stack()[0][3]
        self.setProperty(propertyName, value)
            
    #%%
    @property
    def frequency(self):
        propertyName = stack()[0][3]
        return self.getProperty(propertyName)

    @frequency.setter
    def frequency(self, value):
        propertyName = stack()[0][3]
        self.setProperty(propertyName, value)
        
    #%%
    @property
    def limitMax(self):
        propertyName = stack()[0][3]
        return self.getProperty(propertyName)

    @limitMax.setter
    def limitMax(self, value):
        propertyName = stack()[0][3]
        self.setProperty(propertyName, value)

        
    #%%
    @property
    def limitMin(self):
        propertyName = stack()[0][3]
        return self.getProperty(propertyName)

    @limitMin.setter
    def limitMin(self, value):
        propertyName = stack()[0][3]
        self.setProperty(propertyName, value)

        
    #%%
    @property
    def moveState(self):
        propertyName = stack()[0][3]
        return self.getProperty(propertyName)

        
    #%%
    @property
    def posF(self):
        '''
        read positioning velocity of an axis (values in Hz)
        '''
        propertyName = stack()[0][3]
        return self.getProperty(propertyName)
        
    @posF.setter
    def posF(self, value):
        propertyName = stack()[0][3]
        self.setProperty(propertyName, value)


    #%%
    @property
    def position(self):
        propertyName = stack()[0][3]
        return self.getProperty(propertyName)

        
    #%%
    @property
    def positionEx(self):
        propertyName = stack()[0][3]
        return self.getProperty(propertyName)

        
    #%%
    @property
    def posRange(self):
        propertyName = stack()[0][3]
        return self.getProperty(propertyName)

        
    #%%
    @property
    def refDecel(self):
        propertyName = stack()[0][3]
        return self.getProperty(propertyName)
        
    @refDecel.setter
    def refDecel(self, value):
        propertyName = stack()[0][3]
        self.setProperty(propertyName, value)

        
    #%%
    @property
    def refReady(self):
        '''
        read positioning velocity of an axis (values in Hz)
        '''
        propertyName = stack()[0][3]
        return self.getProperty(propertyName)

        
    #%%
    @property
    def refSwitch(self):
        propertyName = stack()[0][3]
        return self.getProperty(propertyName)
        

    #%%
    @property
    def refSwitchMode(self):
        propertyName = stack()[0][3]
        return self.getProperty(propertyName)
        

    #%%
    @property
    def slowRefF(self):
        propertyName = stack()[0][3]
        return self.getProperty(propertyName)
        
    @slowRefF.setter
    def slowRefF(self, value):
        propertyName = stack()[0][3]
        self.setProperty(propertyName, value)

        
    #%%
    @property
    def targetEx(self):
        propertyName = stack()[0][3]
        return self.getProperty(propertyName)

    @targetEx.setter
    def targetEx(self, position):
        propertyName = stack()[0][3]
        value = c_double(position)
        self.setProperty(propertyName, value)
        

    #%%
    @property
    def targetMode(self):
        propertyName = stack()[0][3]
        return self.getProperty(propertyName)

    @targetMode.setter        
    def targetMode(self, value):
        propertyName = stack()[0][3]
        self.setProperty(propertyName, value)

        
    ### methods ###
    def getProperty(self, propertyName):
        methodName = 'PS10_Get' + propertyName[0].upper() + propertyName[1:]
        getMethod = getattr(self.dll, methodName)
        value = getMethod(self.controller, self.axis)

        self.getReadError(propertyName)

        attributeName = '_' + propertyName
        setattr(self, attributeName, value)
        
        return value

            
    def getReadError(self, propertyName):        
        error = self.dll.PS10_GetReadError(self.controller)

        if error:
            self.logger.error(
                "Error getting axis %s %s: %s",
                self.axis, propertyName, error
            )
            
        return error

        
    def setProperty(self, propertyName, value):        
        methodName = 'PS10_Set' + propertyName[0].upper() + propertyName[1:]
        setMethod = getattr(self.dll, methodName)
        error = setMethod(self.controller, self.axis, value)
        
        if error:
            self.logger.error(
                "Error setting axis %i %s to %s: %i",
                self.axis, propertyName, value, error
            )

        propertyValue = getattr(self, propertyName)
            
        if (value != propertyValue):
            self.logger.error(
                "Axis %i %s value %s differs from %s",
                self.axis, propertyName, value, propertyValue
            )
            
        return error
            
   
    def goRef(self):
        self.logger.debug("Going to axis %i reference position", self.axis)
            
        error = self.dll.PS10_GoRef(self.controller, self.axis, self.refMode)

        if error:
            self.logger.error(
                "Could not go to axis %i reference position in mode %i: %i",
                self.axis, self.refMode, error
            )

        return error


    def goTarget(self):
        error = self.dll.PS10_GoTarget(self.controller, self.axis)

        if error:
            self.logger.error(
                "Could not go to axis %i target: %i",
                self.axis, error
            )

        return error

    #%%
    def motorInit(self):
        '''
        initialize an axis and switch on.

        With this function the axis is completely initialized and afterwards is
        with a current and with active positioning regulator. It must be
        executed after the turning on of the control unit, so that the axis can
        be moved afterwards with the commands REF, PGO, VGO etc. Before the
        following parameters must have been set:
            - limit switch mask,
            - polarity,
            - start regulator parameters.
        '''

        self.logger.debug("Initialising axis %i", self.axis)
        error = self.dll.PS10_MotorInit(self.controller, self.axis)

        if error:
            self.logger.debug(
                "Error initialising axis %i: %i", self.axis, error
            )

        return error


    def motorOn(self):
        self.logger.info("Switching on axis %i", self.axis)
        error = self.dll.PS10_MotorOn(self.controller, self.axis)

        if error:
            self.logger.error(
                "Error switching on axis %i: %i", self.axis, error
            )


    def motorOff(self):
        self.logger.info("Switching off axis %i", self.axis)
        error = self.dll.PS10_MotorOff(self.controller, self.axis)

        if error:
            self.logger.error(
                "Error switching off axis %i: %i", self.axis, error
            )


    def moveAbsolute(self, position):
        self.setTargetAbsolute()

        error = self.dll.PS10_MoveEx(
            self.controller, self.axis, c_double(position), 1
        )
        
        if error:
            self.logger.error(
                "Error moving axis %i to %f: %s", self.axis, position, error
            )
            
        return error

            
    def moveRelative(self, position):
        self.setTargetRelative()

        error = self.dll.PS10_MoveEx(
            self.controller, self.axis, c_double(position), 1
        )
        
        if error:
            self.logger.error(
                "Error moving axis %i a distance of %f: %s",
                self.axis, position, error
            )
            
        return error


    def setTargetAbsolute(self):
        self.targetMode = 1


    def setTargetRelative(self):
        self.targetMode = 0


    def stop(self):
        self.logger.info("Stopping axis %i", self.axis)
        error = self.dll.PS10_Stop(self.controller, self.axis)

        if error:
            self.logger.error("error stopping axis: %s", error)

###############################################################################
class DigitalInput(object):
    def __init__(self, dll, controller, pin):
        self.logger = logging.getLogger('owis')
        self.dll = dll
        self.controller = controller
        self.pin = pin
        self.verbosity = 1
        
        self._previousValue = None
        self._value = None

    @property
    def value(self):
        self._previousValue = self._value
        self._value = self.dll.PS10_GetDigitalInput(self.controller, self.pin)
        error = self.dll.PS10_GetReadError(self.controller)
        
        if error:
            self.logger.error(
                "Error getting digital input from pin %i: %i", self.pin, error
            )
            
        elif self.verbosity == 1:
            if self._value != self._previousValue:
                self.logger.debug(
                    "Digital input pin %i: %i", self.pin, self._value
                )
                
                self._previousValue = self._value

        elif self.verbosity == 2:
            self.logger.debug(
                "Digital input pin %i: %i", self.pin, self._value
            )
               
        return self._value


    @value.setter
    def value(self, value):
        if hasattr(self.dll, 'digitalInput'):
            self._value = value
            self.dll.digitalInput[self.pin - 1] = value
        

###############################################################################
class DigitalOutput(object):
    def __init__(self, dll, controller, pin):
        self.logger = logging.getLogger('owis')

        self.dll = dll
        self.controller = controller
        self.pin = pin
        self._previousValue = 0
        self._value = 0
        self.verbosity = 2

    ### properties
    @property
    def value(self):
        self._previousValue = self._value
        self._value = self.dll.PS10_GetDigitalOutput(self.controller, self.pin)
        error = self.dll.PS10_GetReadError(self.controller)
        
        if error:
            self.logger.error(
                "Error getting digital output %i: %i", self.pin, error
            )

        elif self.verbosity == 1:
            if self._value != self._previousValue:
                self.logger.debug(
                    "Digital output pin %i: %i -> %i",
                    self.pin, self._previousValue, self._value
                )

        elif self.verbosity == 2:
            self.logger.debug(
                "Digital output pin %i: %s", self.pin, self._value
            )
                
        return self._value

    @value.setter
    def value(self, state):
        error = self.dll.PS10_SetDigitalOutput(
            self.controller, self.pin, state
        )
        
        if error:
            self.logger.error(
                "Error setting digital output pin %i: %s", self.pin, error
            )
        else:
            self._value = state
            self.logger.debug("Digital output pin %i: %s", self.pin, state)

###############################################################################
class PwmOutput(object):
    def __init__(self, dll, controller, pin):
        self.logger = logging.getLogger('owis')

        self.dll = dll
        self.controller = controller
        self.pin = pin

    ### properties
    @property
    def value(self):
        self._value = self.dll.PS10_GetPwmOutput(self.controller, self.pin)
        error = self.dll.PS10_GetReadError(self.controller)
        
        if error:
            self.logger.error(
                "Error getting PWM output from pin %i: %i", self.pin, error
            )
        else:
            self.logger.debug("PWM pin %i: %s", self.pin, self._value)
                
        return self._value        

    @value.setter
    def value(self, value):

        error = self.dll.PS10_SetPwmOutput(self.controller, self.pin, value)

        if error:
            self.logger.error(
                "Error setting PWM pin %i to %s: %i", self.pin, value, error)
        else:
            self.logger.debug("PWM pin %i output: %s", self.pin, value)
            
###############################################################################
class PS10(object):
    """
    Hardware controller interface.
    """
    
    MAX_TRY = 3

    def __init__(self, filename):
        self.logger = logging.getLogger('owis')
        self.logger.info("Starting OWIS PS10-32 controller")

        with open(filename) as f:    
            self.paraDict = yaml.load(f)

        self.hardwareParameter = self.paraDict['hardware']

        self.com = None
        self.controller = 1
        self.N_aIn = 4
        self.N_digOut = 5
        self.N_digIn = 4
        self.N_pwm = 2

        '''
            0: success
            -1: function error
            -2: communication error
            -3: syntax error
        '''
        self.error = 0

        self._emergency = 0
        self._emergencyPressed = False
        self._emergencyReleased = False
        self._outputMode = 0
        self._prevEmergency = 0

        self.port = None
        self._slaves = None
        self._serialNumber = 20 * ' '

        self.AXIS_LRT = 1
        self.AXIS_DRT = 2
 
        self.conv_axis = {self.AXIS_LRT : 1e-4, self.AXIS_DRT : 9e-3}

        self.reference = Position()

        self.referenceState = 0
        self.maxReferenceState = 0
        self.needReference = True
        self.needVacuum = True
        self.offsetMark = 0
        self.maxPosition = 1e3

        self.detectPort()

        # self.com = 5
        
        self.baudrate = self.hardwareParameter['baudrate']
        self.dllfile = self.hardwareParameter['dllfile']
        self.logging = self.hardwareParameter['logging']
        self.logfile = self.hardwareParameter['logfile']
        self.timeout = self.hardwareParameter['timeout']

        if self.com is not None:

            self.loadDLL(self.dllfile)
            
            interface = 0
    
            self.connect(
                self.controller, interface, self.com, self.baudrate,
                self.timeout
            )

        if self.error or (self.com is None):
            self.logger.warning("Switching to hardware emulator")
            self.dll = PS10_Emulator()

        self.setCanOpenSlave(101, 1)
        self.getCanOpenSlave()

        if self.logging:
            self.initLogging()
        
        self.initAxes()
        self.initAnalogInput()
        self.initDigitalInput()
        self.initDigitalOutput()

        self.vacuumOutput = self.digitalOutput[0]
        self.vacuumInput = self.digitalInput[0]
        
        self.axes[0].motorInit()
        self.axes[1].motorInit()

        # using the method call leads to strange conversion erros
        self.axes[0].limitMax = 700000
        self.axes[0].limitMin = 0
        
        # set conversion
        # self.axes[0].conversion = 1E-4
        # self.axes[1].conversion = 9E-3

        self.axes[0].offsetMark = 0.
        self.axes[1].offsetMark = 0.


    def initAnalogInput(self):
        self.analogInput = []
        
        for i in range(self.N_aIn):
            analogInput = AnalogInput(self.dll, self.controller, i + 1)
            self.analogInput.append(analogInput)

    def initAxes(self):
        self.axes = []
        
        axesDict = self.paraDict['hardware']['axes']
        
        for a in axesDict:
            index = a['index']
            axisName = "axis" + a['name']
            
            axis = Axis(self.dll, self.controller, index)
            
            setattr(self, axisName, axis)
            self.axes.append(axis)

            for key in a.keys():            
                setattr(axis, key, a[key])

        for a in axesDict:
            axisName = "axis" + a['name']
            axis = getattr(self, axisName)
            
            for key in a.keys():            
                value = getattr(axis, key)

                self.logger.debug('%s %s = %s', axisName, key, value)
        

    def initDigitalInput(self):
        self.digitalInput = []
        
        for i in range(self.N_digIn):
            digInput = DigitalInput(self.dll, self.controller, i + 1)
            self.digitalInput.append(digInput)


    def initDigitalOutput(self):
        self.digitalOutput = []
        
        for i in range(self.N_digOut):
            output = DigitalOutput(self.dll, self.controller, i + 1)
            self.digitalOutput.append(output)

            
    def initLogging(self):
        self.logger.info(
            "Start logging to %s", self.logfile
        )
        
        filename = c_char_p(self.logfile)

        try:
            error = self.dll.PS10_LogFile(self.controller, 1, filename, 0, 1)
        except WindowsError:
            error = 99

        if error:
            self.logger.error(
                "Could not start logging to %s: %i", filename, error
            )


    #%% properties
    @property
    def checkSumMem(self):
        self._checkSum = self.dll.PS10_CheckMem(self.controller)
        error = self.dll.PS10_GetReadError(self.controller)

        if error:
            self.logger.error("Error getting memory check sum: %i", error)
        
        return self._checkSum

    #%%
    @property
    def emergency(self):
        self._prevEmergency = self._emergency
        self._emergency = self.dll.PS10_GetEmergencyInput(self.controller)

        if self._prevEmergency == 0 and self._emergency == 1:
            self._emergencyReleased = True
            
            self.logger.warning('Emergency input released')
        
        elif self._prevEmergency == 1 and self._emergency == 0:
            self._emergencyPressed = True

            self.logger.warning('Emergency input pressed')

        return self._emergency

    #%%
    @property
    def emergencyPressed(self):
        value = self._emergencyPressed
        self._emergencyPressed = False
        return value

    #%%
    @property
    def emergencyReleased(self):
        value = self._emergencyReleased
        self._emergencyReleased = False
        return value

    #%%
    @property
    def outputMode(self):
        self.logger.debug('Getting output mode')

        mode = self.dll.PS10_GetOutputMode(self.controller)
        error = self.dll.PS10_GetReadError(self.controller)
        
        if error:
            self.logger.error("Error getting output mode")
        else:
            self._outputMode = mode
            
            if mode == 0:
                self.logger.debug(
                    "pin 1: digital SPS-output," +
                    "pin 2: digital SPS-output"
                )
            elif mode == 1:
                self.logger.debug(
                    "pin 1: digital SPS-output," +
                    "pin 2: PWM-output"
                )
            elif mode == 2:
                self.logger.debug(
                    "pin 1: PWM-output," +
                    "pin 2: PWM-output")
                
        return mode

    @outputMode.setter
    def outputMode(self, mode):
        self.error = self.dll.PS10_SetOutputMode(self.controller, mode)

        if self.error:
            self.logger.error("Error setting output mode to %s", mode)
        else:
            self._outputMode = self.dll.PS10_GetOutputMode(self.controller)

    #%%
    @property
    def serialNumber(self):
        strBuffer = 20 * ' '
        bufSize = self.dll.PS10_GetSerNumber(1, strBuffer, 20)
        
        self._serialNumber = strBuffer[:bufSize]

        return self._serialNumber


    #%%
    @property
    def slaves(self):
        self._slaves = self.dll.PS10_GetSlaves(self.controller)
        error = self.dll.PS10_GetReadError(self.controller)

        if error:
            self.logger.error("Error getting slaves: %i", error)

        return self._slaves


    #%% methods 
    def connect(self, controller, interface, com, baud, timeout):
        self.logger.debug("Connecting to PS10")
        
        self.error = self.dll.PS10_Connect(
            controller, interface, com, baud, timeout,
            0, 0, 0
        )

        if self.error:
            self.logger.error("Could not connect to PS10: %s", self.error)
        else:
            self.controller = controller
            self.interface = interface
            
            self.logger.debug(
                "Connected to PS10(%s, %s)", controller, interface
            )
            
        return self.error

        
    def detectPort(self):
        ports = list(serial.tools.list_ports.comports())
        self.port = None
        self.com = None

        if len(ports) == 0:
            self.logger.warning("Could not find any serial device!")

        for p in ports:
            if 'STMicroelectronics Virtual COM Port' in p[1]:
                self.logger.debug(p[1])
                self.logger.debug(p[2])
                self.com = int(p[0][3])

                self.port = p                
                
        return self.com


    def loadDLL(self, dllFile):
        self.logger.debug("Loading %s", dllFile)
       
        if os.path.exists(dllFile):
            self.dll = WinDLL(dllFile)
        else:
            self.logger.error("Could not find %s", dllFile)

        self.dll.PS10_GetSerNumber.argtypes = [c_int, c_char_p, c_int]
        self.dll.PS10_GetPositionEx.restype = c_double


    def moveRef(self):
        self.logger.info("Going to reference position")

        error = self.axisLRT.goRef()
        
        if error:
            self.logger.error(
                "Setting axis 1 reference position failed: %i",
                error
            )
            
            # return

        time.sleep(1.0)        
        error = self.axisDRT.goRef()        

        if error:
            self.logger.error(
                "Setting axis 2 reference position failed: %i",
                error
            )
            
            # return

        while self.axisLRT.moveState:
            self.logger.debug("LRT move state: %i", self.axisLRT.moveState)
            time.sleep(0.1)

        while self.axisDRT.moveState:
            self.logger.debug("DRT move state: %i", self.axisDRT.moveState)
            time.sleep(0.1)

        '''
        while not self.axisLRT.refReady:
            time.sleep(0.1)

        while not self.axisDRT.refReady:
            time.sleep(0.1)
        '''

        self.logger.debug("DRT axis ready: %i", self.axisDRT.refReady)

        self.reference.lrt = self.getPosition(self.AXIS_LRT)
        self.reference.drt = self.getPosition(self.AXIS_DRT)

        self.logger.info("Reference position reached")

        self.getCurrentPosition()
        
        self.logger.info(
            "Position: %i, %i", self.axisLRT.position, self.axisDRT.position
        )

        self.logger.info(
            "Position: %i, %i", self.axisLRT.positionEx, self.axisDRT.positionEx
        )

        
    def getCurrentPosition(self):
        lrt = self.getPosition(self.AXIS_LRT)
        drt = self.getPosition(self.AXIS_DRT)

        self.logger.debug(
            "current position: %0.1f %s, %0.1f %s",
            lrt, self.axisLRT.unit,
            drt, self.axisDRT.unit
        )

        return lrt, drt
    
    
    def getPosition(self, axis):
        position = self.dll.PS10_GetPosition(self.controller, axis)
        error = self.dll.PS10_GetReadError(self.controller)

        position *= self.conv_axis[axis]

        if axis == self.AXIS_DRT:
            position += self.offsetMark
        
        if error:
            self.logger.error("Error getting axis %i position", axis)
            
        return position


    def checkReference(self, axis):
        self.referenceState &= (0 << (axis-1))
        '''
        reset reference state for axis:
            - workaround to keep reference state even if the axis was shut down
              due to light curtain obstruction
            - the real reference state will be ignored once it was set at least
              one time
            - this will also turn off software limits
        '''
        self.referenceState |= (self.maxReferenceState << (axis-1)) 

        if self.needReference:
            refState = self.dll.PS10_GetRefReady(self.controller, axis)
            self.maxReferenceState |= (refState << (axis-1))
            # set reference state for axis
            self.referenceState |= (refState << (axis-1))
        else:
            self.maxReferenceState |= (1 << (axis-1))
            self.referenceState |= (1 << (axis-1))

        return self.maxReferenceState & (1 << (axis - 1)) > 0


    def moveRelative(self, axis, position, wait = False):
        self.checkReference(axis)
        
        self.logger.info(
            "Moving axis %s a distance of %s %s",
            axis, position, self.axes[axis-1].unit
        )

        if(
            self.needVacuum and
            axis == self.AXIS_DRT and (
                self.vacuumOutput.value == 0 or
                self.vacuumInput.value == 0
            )
        ):
            # if no vacuum, don't move DRT
            self.logger.warning("Vacuum needed for axis %s", axis)
            return

        if(
            axis == self.AXIS_LRT and
            (self.getPosition(axis) + position) > self.maxPosition
        ):
            # software limit of LRT movement
            self.logger.warning("movement would hit limit ... abort")
            return

        if self.axes[axis-1].moveState > 0:
            # if axis is moving, don't do anything
            self.logger.warning("axis %s is already moving", axis)
            return

        if not self.referenceState & (1 << (axis-1)):
            # if no reference for axis is set, don't move
            self.logger.warning("no reference for axis %s", axis)
            return


        self.axes[axis - 1].moveRelative(position)
            

        if wait:
            while self.axes[axis-1].moveState != 0:
                pass


    def moveAbsolute(self, axis, position, wait = False):
        self.checkReference(axis)

        self.logger.info(
            "moving axis %s a distance of %s %s",
            axis, position, self.axes[axis-1].unit
        )

        if(
            self.needVacuum and
            axis == self.AXIS_DRT and
            (self.vacuumOutput.value == 0 or
            self.vacuumInput.value == 0)
        ): # if no vacuum, don't move DRT
            self.logger.warning("vacuum needed for axis %s", axis)
            return

        if axis == self.AXIS_LRT and position > self.maxPosition:
            # software limit of LRT movement
            self.logger.warning(
                "movement would hit software limit %s abort",
                self.maxPosition
            )
            return

        if self.axes[axis - 1].moveState > 0:
            # if axis is moving, don't do anything
            self.logger.warning("axis %s is already moving", axis)
            return

        if not self.referenceState & (1 << (axis-1)):
            # if no reference for axis is found, don't move
            self.logger.error("no reference for axis %s", axis)
            return

        if axis == self.AXIS_DRT: # if DRT apply position offset
            position -= self.offsetMark

        self.axes[axis - 1].moveAbsolute(position)

        if wait:
            while self.getMoveState(axis) != 0:
                pass


    def setCanOpenSlave(self, slaveNumber, slaveID):
        self.slaveNumber = slaveNumber
        self.slaveID = slaveID

        self.logger.debug(
            "setting CanOpen slave: (" +
            str(slaveNumber) + ", " +  str(slaveID) + ")"
        ) 

        
        error = self.dll.PS10_SetCanOpenSlave(slaveNumber, slaveID)
        
        if error:
            self.logger.error("Error:", error)


    def getCanOpenSlave(self, slaveNumber = None):

        if slaveNumber == None:
            slaveNumber = self.slaveNumber
            
        if slaveNumber > 100:
            self.slaveID = self.dll.PS10_GetCanOpenSlave(slaveNumber)
            error = self.dll.PS10_GetReadError(self.controller)
        else:
            error = -4

        if error:
            self.logger.error("Error getting slaveID:", error)

        return self.slaveID


    def disconnect(self):
        error = self.dll.PS10_Disconnect(self.controller)

        self.logger.debug(
            "Disconnecting from PS10 controller %s", self.controller
        )

        if error:
            self.logger.error("Error disconnecting PS10 controller: %s", error)
            
        return error


    def simpleConnect(self, controller):
        self.logger.debug("Connecting to PS10")
        
        serialNumber = '15050140'
        
        self.error = self.dll.PS10_SimpleConnect(
            controller, serialNumber
        )

        if self.error:
            self.logger.warning("Could not connect to PS10: %s", self.error)
        else:
            self.controller = controller
            
            self.logger.debug(
                "Connected to PS10(%s, %s)", controller, serialNumber
            )
            
        return self.error
###############################################################################
class PS10_Emulator:
    """
    emulation of essential PS10 DLL commands
    """

    def __init__(self):
        self.logger = logging.getLogger('owis')

        self.jobs = []
        self.voltage = 0.0
        self.refMode = 4
        
        self.digitalInput = [1, 1, 1, 1, 1]
        self.digitalOutput = [0, 0, 0, 0, 0]

        self._accel = [0, 0]
        self._conversion = [1e-4, 9e-3]
        self.errorState = [0, 0]
        self._fastRefF = [0, 0]
        self._frequency = [0, 0]
        self._limitMax = [0, 0]
        self._limitMin = [0, 0]
        self._moveState = [0, 0]
        self._outputMode = 0
        self._posF = [0, 0]
        self._position = [0., 0.]
        self._pwmOutput = 0
        self._refReady = [0, 0]
        self._slowRefF = [0, 0]
        self._targetMode = 0


    def goRefWorker(self, axis):
        self.logger.info('moving axis %i to reference', axis)

        time.sleep(1)

        self._moveState[axis - 1] = 0
        self._refReady[axis - 1] = 1
        
        self.logger.info('finished moving axis %i to reference', axis)

    def PS10_CheckMem(self, controller):
        return 0

    def PS10_Connect(
        self, controller, interface, com, baud, handshake, bit1, bit2, bit3
    ):
        return 0
    
    def PS10_Disconnect(self, controller):
        for job in self.jobs:
            job.join()
            
        return 0

        
    def PS10_Stop(self, controller, axis):
        return False

    #%%
    def PS10_GetAccel(self, controller, axis):
        return self._accel[axis - 1]

    def PS10_SetAccel(self, controller, axis, value):
        self._accel[axis - 1] = value
    
    #%%
    def PS10_GetAnalogInput(self, controller, pin):
        value = self.voltage
        return value

    #%%
    def PS10_GetCanOpenSlave(self, slaveNumber):
        return 0

    def PS10_SetCanOpenSlave(self, slaveNumber, slaveID):
        return 0
    
    #%%
    def PS10_GetDigitalInput(self, controller, pin):
        return self.digitalInput[pin - 1]

    #%%
    def PS10_GetDigitalOutput(self, controller, pin):
        return self.digitalOutput[pin - 1]

    def PS10_SetDigitalOutput(self, controller, pin, state):
        self.digitalOutput[pin - 1] = state
        return 0

    #%%
    def PS10_GetEmergencyInput(self, controller):
        return False

    #%%
    def PS10_GetErrorState(self, controller, axis):
        return self.errorState[axis - 1]

    #%%
    def PS10_GetF(self, controller, axis):
        return self._frequency[axis - 1]

    def PS10_SetF(self, controller, axis, value):
        self._frequency[axis - 1] = value

    #%%
    def PS10_GetFastRefF(self, controller, axis):
        return self._fastRefF[axis - 1]

    def PS10_SetFastRefF(self, controller, axis, value):
        self._fastRefF[axis - 1] = value

    #%%%
    def PS10_GetLimitMax(self, controller, axis):
        return self._limitMax[axis - 1]

    def PS10_SetLimitMax(self, controller, axis, value):
        self._limitMax[axis - 1] = value

    #%%
    def PS10_GetLimitMin(self, controller, axis):
        return self._limitMin[axis - 1]

    def PS10_SetLimitMin(self, controller, axis, value):
        self._limitMin[axis - 1] = value

    #%%
    def PS10_GetMoveState(self, controller, axis):
        return self._moveState[axis - 1]
        
    #%%
    def PS10_GetOutputMode(self, controller):
        return self._outputMode

    def PS10_SetOutputMode(self, controller, mode):
        self._outputMode = mode

    #%%
    def PS10_GetPosF(self, controller, axis):
        return self._posF[axis - 1]

    def PS10_SetPosF(self, controller, axis, value):
        self._posF[axis - 1] = value

    #%%
    def PS10_GetPosition(self, controller, axis):
        position = self._position[axis - 1]
        return position

    #%%
    def PS10_GetPositionEx(self, controller, axis):
        return 0

    #%%
    def PS10_GetPwmOutput(self, controller, pin):
        return self._pwmOutput

    def PS10_SetPwmOutput(self, controller, pin, value):
        self._pwmOutput = value
        return 0
    
    #%%
    def PS10_GetReadError(self, controller):
        error = False
        return error

    #%%
    def PS10_GetRefDecel(self, controller, axis):
        return 0
        
    def PS10_SetRefDecel(self, controller, axis, value):
        self._refDecel = value

        
    def PS10_GetRefReady(self, controller, axis):
        return self._refReady[axis - 1]

    def PS10_GetRefSwitch(self, controller, axis):
        return 0

    def PS10_GetRefSwitchMode(self, controller, axis):
        return 0

    #%%
    def PS10_GetSlaves(self, controller):
        return 0

    #%%
    def PS10_GetSlowRefF(self, controller, axis):
        return self._slowRefF[axis - 1]

    def PS10_SetSlowRefF(self, controller, axis, value):
        self._slowRefF[axis - 1] = value

    #%%
    def PS10_GoRef(self, controller, axis, mode):

        self._moveState[axis - 1] = 3

        t = threading.Thread(
            target = self.goRefWorker, args = (axis,)
        )

        t.start()

        return 0


    def PS10_MotorInit(self, controller, axis):
        return 0

    def PS10_MotorOff(self, controller, axis):
        pass


    def PS10_MoveEx(self, controller, axis, position, flag):
        if self._targetMode == 0:
            self._position[axis - 1] += position.value
        elif self._targetMode == 1:
            self._position[axis - 1] = position.value
            
        return 0


    def PS10_SetCoversion(self, controller, axis, vaule):
        return 0

        
    def PS10_GetTargetMode(self, controller, axis):
        return self._targetMode
        
    def PS10_SetTargetMode(self, controller, axis, value):
        self._targetMode = value
        return 0

###############################################################################
def oldTests(self):



    ### SPS outputs

    # set both outputs to SPS
    # ps10.outputMode = 0
    
    #ps10.motorOff(1)
    #ps10.motorOff(2)
    ps10.getRefSwitch(1, True)
    ps10.getRefSwitch(2, True)

    ps10.getRefSwitchMode(1, True)
    ps10.getRefSwitchMode(2, True)

    logger.info(
        "Fast Ref DRT %s", ps10.dll.PS10_GetFastRefF(ps10.controller, 2)
    )
    
    logger.info(
        "Slow Ref DRT %s", ps10.dll.PS10_GetSlowRefF(ps10.controller, 2)
    )

    logger.info(
        "Fast Ref LRT %s", ps10.dll.PS10_GetFastRefF(ps10.controller, 1)
    )
    
    logger.info(
        "Slow Ref LRT %s", ps10.dll.PS10_GetSlowRefF(ps10.controller, 1)
    )
    
    logger.info(
        "Speed LRT %s", ps10.dll.PS10_GetF(ps10.controller, 1)
    )
    logger.info(
        "Accel LRT %s", ps10.dll.PS10_GetAccel(ps10.controller, 1)
    )

    logger.info("Speed DRT %s", ps10.dll.PS10_GetF(ps10.controller, 1))
    logger.info("Accel DRT %s", ps10.dll.PS10_GetAccel(ps10.controller, 1))

#    ps10.dll.PS10_SetLimitControl(ps10.controller,1,0b11)
#    ps10.dll.PS10_SetLimitControl(ps10.controller,2,0b11)
        
    logger.info("POS LRT %s", ps10.getPosition(1))
#    timestamp(ps10.getPosition(2))
    ps10.moveRef(True)
    logger.info("POS LRT %s", ps10.getPosition(1))
#    timestamp(ps10.getPosition(2))
    ps10.moveRelative(1, 5)
#    ps10.moveRelative(2,90)
    logger.info("POS LRT %s", ps10.getPosition(1))
    #timestamp(ps10.getPosition(2))
    # timestamp(bin(ps10.dll.PS10_GetLimitSwitch(ps10.controller,1)))
    #timestamp(bin(ps10.dll.PS10_GetLimitSwitch(ps10.controller,2)))
    
    logger.info(ps10.dll.PS10_SetLimitMax(ps10.controller, 1, 700000))
    logger.info(ps10.dll.PS10_SetLimitMin(ps10.controller, 1, -10))

    # timestamp(ps10.dll.PS10_GetLimitMin(ps10.controller,1))
    #timestamp(ps10.dll.PS10_GetLimitMin(ps10.controller,2))
    # timestamp(ps10.dll.PS10_GetLimitMax(ps10.controller,1))
    
    # timestamp(ps10.dll.PS10_SetLimitMax(ps10.controller,2,40000))
    # timestamp(ps10.dll.PS10_SetLimitMin(ps10.controller,2,-40000))

    
    # timestamp(ps10.dll.PS10_GetLimitMin(ps10.controller,1))
    #timestamp(ps10.dll.PS10_GetLimitMin(ps10.controller,2))
    # timestamp(ps10.dll.PS10_GetLimitMax(ps10.controller,1))
    #timestamp(ps10.dll.PS10_GetLimitMax(ps10.controller,2))


    # timestamp(ps10.getPosRange(1))
    # timestamp(ps10.getPosRange(2))
    
    # timestamp(ps10.dll.PS10_GetPosition(ps10.controller,1))
    #timestamp(ps10.dll.PS10_GetPosition(ps10.controller,2))
    
    ps10.moveAbsolute(1, 65, True)
    #ps10.moveAbsolute(2,355,True)
    #ps10.moveRef(True)
    ps10.moveAbsolute(1, 30, True)
    ps10.moveAbsolute(2, 160, True)
    #ps10.moveAbsolute(2,365,True)
    logger.info("POS LRT %s", ps10.getPosition(1))
    logger.info("POS DRT %s", ps10.getPosition(2))
    #time.sleep(5)
    # timestamp(1.0*ps10.dll.PS10_GetPosition(ps10.controller,1)/1e4)
    # timestamp(1.0*ps10.dll.PS10_GetPosition(ps10.controller,2)*360/4e4)
    
    #ps10.moveAbsolute(2,0)
    
    #time.sleep(20)
    #timestamp(1.0*ps10.dll.PS10_GetPosition(ps10.controller,2)*360/4e4)

    ps10.motorOff(1)
    ps10.motorOff(2)
    
    '''
    ps10.getRefSwitch(1, True)
    ps10.getRefSwitch(2, True)

    ps10.getRefSwitchMode(1, True)
    ps10.getRefSwitchMode(2, True)

    ps10.getPositionEx(1)
    ps10.getPositionEx(2)

    ps10.moveRef()

    ps10.moveRelative(1, 40.)
    '''
