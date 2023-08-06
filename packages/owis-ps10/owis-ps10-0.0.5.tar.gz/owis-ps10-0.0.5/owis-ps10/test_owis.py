### imports ###################################################################
import logging
import time
import unittest

### local imports #############################################################
import owis

###############################################################################
class OwisTest(unittest.TestCase):

    logger = logging.getLogger('owis_test')

    ps10 = owis.PS10('..\\config\\company_owis.cfg')
    
    analogInputs = [0, 0, 0, 0]
    com = 3
    comDesc = 'STMicroelectronics Virtual COM Port (COM3)'
    comStr = 'COM3'
    controller = 1
    digitalInputs = [0, 1, 1, 1]
    digitalOutputOff = [0, 0, 0, 0, 0]
    digitalOutputOn = [1, 1, 1, 1, 1]
    # usb = 'USB VID:PID=0483:5740 SNR=DEMO_1'
    usb = 'USB VID:PID=0483:5740 SER=DEMO_1 LOCATION=1-5'


    def setUp(self):
        pass

    '''
    def test_00_getBoardVersion(self):
        version = c_char_p()

        self.ps10.dll.PS10_GetBoardVersion.argtypes = [
            c_long, c_char_p, c_long
        ]
        
        length = self.ps10.dll.PS10_GetBoardVersion(1, version, 25)
        print(length, version)
    '''

    @unittest.skip('not working yet')
    def test_00_checkMem(self):
        checkSum = self.ps10.checkSumMem
        print(checkSum)
        

    def test_01_detectPort(self):
        self.ps10.detectPort()
        port = self.ps10.port

        if port is not None:        
            self.assertEqual(port[0], self.comStr)
            self.assertEqual(port[1], self.comDesc)
            self.assertEqual(port[2], self.usb)


    def test_02_motorInit(self):
        for i in range(2):
            error = self.ps10.axes[i].motorInit()
            
            self.assertEqual(error, 0)


    def test_03_connect(self):
        self.assertEqual(self.ps10.disconnect(), 0)
        
        interface = 0
        baud = 9600
        handshake = 0

        error = self.ps10.connect(
            self.controller, interface, self.com, baud, handshake
        )        
        
        self.assertEqual(error, 0)

    #%% test inputs
    def test_04_getAnalogInput(self):
        analogInputs = []
        
        for i in range(4):
            value = self.ps10.analogInput[i].value

            analogInputs.append(value)

        self.assertEqual(analogInputs, self.analogInputs)


    def test_05_getDigitalInput(self):
        digitalInputs = []

        for i in range(4):
            value = self.ps10.digitalInput[i].value

            digitalInputs.append(value)
            
        self.assertEqual(digitalInputs, self.digitalInputs)

    #%% test outputs
    def test_06_outputMode(self):
        self.ps10.outputMode = 2
        self.assertEqual(self.ps10.outputMode, 2)

        self.ps10.outputMode = 1
        self.assertEqual(self.ps10.outputMode, 1)

        self.ps10.outputMode = 0
        self.assertEqual(self.ps10.outputMode, 0)

    #%% test digital output
    def test_07_digitalOutputAllOn(self):
        outputList = []

        for i in range(5):
            self.ps10.digitalOutput[i].value = 1
        
        for i in range(5):
            value = self.ps10.digitalOutput[i].value
            outputList.append(value)

        self.assertEqual(outputList, self.digitalOutputOn)

            
    def test_08_getDigitalOutputAllOff(self):
        outputList = []

        for i in range(5):
            self.ps10.digitalOutput[i].value = 0
        
        for i in range(5):
            value = self.ps10.digitalOutput[i].value
            outputList.append(value)

        self.assertEqual(outputList, self.digitalOutputOff)


    def test_09_axis(self):
        
        self.ps10.axes[0].f = 20000
        self.ps10.axes[0].limitMax = 700000
        self.ps10.axes[0].limitMin = 0
        self.ps10.axes[0].fastRefF = -50000
        self.ps10.axes[0].slowRefF = 2500
        self.ps10.axes[0].posF = 75000
        self.ps10.axes[0].accel = 250000
        # self.ps10.axes[0].conversion = 1e-4

        
        self.assertEqual(self.ps10.axes[0].f, 20000)
        self.assertEqual(self.ps10.axes[0].limitMax, 700000)
        self.assertEqual(self.ps10.axes[0].limitMin, 0)
        self.assertEqual(self.ps10.axes[0].fastRefF, -50000)
        self.assertEqual(self.ps10.axes[0].slowRefF, 2500)
        self.assertEqual(self.ps10.axes[0].posF, 75000)
        self.assertEqual(self.ps10.axes[0].accel, 250000)
        # self.assertEqual(self.ps10.axes[0].conversion, 1e-4)

    def test_10_axis(self):
        self.ps10.axes[1].f = 20000
        # self.ps10.axes[1].limitMax = 7000000
        # self.ps10.axes[1].limitMax = 700000
        # self.ps10.axes[1].limitMin = 0
        self.ps10.axes[1].fastRefF = -5000
        # self.ps10.axes[1].slowRefF = 2500
        # self.ps10.axes[1].posF = 75000
        # self.ps10.axes[1].accel = 250000
        # self.ps10.axes[0].conversion = 1e-4
        
        self.assertEqual(self.ps10.axes[1].f, 20000)
        # self.assertEqual(self.ps10.axes[1].limitMax, 0)
        # self.assertEqual(self.ps10.axes[1].limitMin, 0)
        # self.assertEqual(self.ps10.axes[1].fastRefF, -5000)
        # self.assertEqual(self.ps10.axes[1].slowRefF, 2500)
        # self.assertEqual(self.ps10.axes[1].posF, 75000)
        # self.assertEqual(self.ps10.axes[1].accel, 250000)

    def test_15_goRef(self):
        for iAxis in range(2):
            refReady = self.ps10.axes[iAxis].refReady
            self.assertEqual(refReady, 0)

            error = self.ps10.axes[iAxis].goRef()
            self.assertEqual(error, 0)

            # iCounter = 0
        
            while (
                # iCounter < 100 and
                self.ps10.axes[iAxis].moveState == 3
            ):
                
                time.sleep(0.1)
                # iCounter += 1
                

            refReady = self.ps10.axes[iAxis].refReady
            self.assertEqual(refReady, 1)
        

    def test_16_getPosition(self):
        lrt = self.ps10.getPosition(self.ps10.AXIS_LRT)
        drt = self.ps10.getPosition(self.ps10.AXIS_DRT)

        self.assertEqual(lrt, 0.)
        self.assertEqual(drt, 0.)


    def test_99_disconnect(self):
        self.assertEqual(self.ps10.disconnect(), 0)


    def tearDown(self):
        pass


###############################################################################
if __name__ == '__main__':
    
    ### configuration
    loggingLevel = logging.DEBUG
    # loggingLevel = logging.INFO

    ### set logging
    logging.basicConfig(level = loggingLevel)
    logger = logging.getLogger()

    ### run unit test
    unittest.main()


        
