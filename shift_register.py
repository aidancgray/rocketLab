#!/usr/bin/python3
# shift_register.py
# 04/10/2023
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# Shift Register (shiftRegister) class. 
###############################################################################
# WiringPi shiftOut function:
#   shiftOut(dataPin, clockPin, order[LSBFIRST or MSBFIRST], data) 
#
# Shift out 123 (b1111011, byte 0-255) to data pin 1, clock pin 2 
#   wiringpi.shiftOut(1, 2, 0, 123)
###############################################################################

import logging
import asyncio
import wiringpi as gpio

LOW = 0
HIGH = 1
INPUT = 0
OUTPUT = 1
SLEEP_TIME = 0.000001
uSLEEP_TIME = 1

class GPIO_to_cRIO:
    def __init__(self, qXmit, 
                 inputPin, clockPin, latchPin, clearPin, outEnPin, 
                 snapFullPin, snapEmptyPin, snapReadPin,
                 order, clockTime=0):
        self.logger = logging.getLogger('fodo')
        self.qXmit = qXmit
        self.inputPin = inputPin
        self.clockPin = clockPin
        self.latchPin = latchPin
        self.clearPin = clearPin
        self.outEnPin = outEnPin
        self.snapFullPin = snapFullPin
        self.snapEmptyPin = snapEmptyPin
        self.snapReadPin =  snapReadPin
        self.order = order
        self.clockTime = clockTime

        gpio.wiringPiSetup()
        self.setupShiftPins()
        self.setDefaultStates()
        self.clearData()

    async def start(self):
        while True:
            if not self.qXmit.empty():
                data = await self.qXmit.get()
                self.logger.debug(f'{data}')
                self.handleData(data)
            await asyncio.sleep(SLEEP_TIME)

    def handleData(self, data):
        for n in range(len(data)):
            photon = data[n]
            x = photon[0]
            y = photon[1]

            self.shiftDataOut(y)
            self.shiftDataOut(x)
            self.latchData()
            
            self.writeData(self.outEnPin, LOW)
            #self.writeData(self.snapFullPin, HIGH)
            #self.writeData(self.snapEmptyPin, LOW)

            # Clock the SNAP_FIFO_READ
            self.writeData(self.snapReadPin, HIGH)
            gpio.delayMicroseconds(uSLEEP_TIME)
            self.writeData(self.snapReadPin, LOW)

            #self.writeData(self.snapEmptyPin, HIGH)
            #self.writeData(self.snapFullPin, LOW)
            self.writeData(self.outEnPin, HIGH)
            
    def setPinMode(self, pin, mode):
        gpio.pinMode(pin, mode)

    def setupShiftPins(self):
        self.setPinMode(self.inputPin, OUTPUT)
        self.setPinMode(self.clockPin, OUTPUT)
        self.setPinMode(self.latchPin, OUTPUT)
        self.setPinMode(self.clearPin, OUTPUT)
        self.setPinMode(self.outEnPin, OUTPUT)
        self.setPinMode(self.snapFullPin, OUTPUT)
        self.setPinMode(self.snapEmptyPin, OUTPUT)
        self.setPinMode(self.snapReadPin, OUTPUT)

    def writeData(self, pin, state):
        gpio.digitalWrite(pin, state)

    def shiftDataOut(self, data):
        self.writeData(self.clockPin, LOW)
        try:
            gpio.shiftOut(self.inputPin, self.clockPin, self.order, data)
        except:
            self.logger.error(f'gpio.shiftOut() failed')

    def latchData(self):
        gpio.digitalWrite(self.latchPin, LOW)
        gpio.digitalWrite(self.latchPin, HIGH)
        gpio.digitalWrite(self.latchPin, LOW)

    def clearData(self):
        self.writeData(self.clearPin, HIGH)
        self.writeData(self.clearPin, LOW)
        self.writeData(self.clearPin, HIGH)

    def setDefaultStates(self):
        self.writeData(self.inputPin, LOW)
        self.writeData(self.clockPin, LOW)
        self.writeData(self.latchPin, LOW)
        self.writeData(self.clearPin, HIGH)
        self.writeData(self.outEnPin, HIGH)
        self.writeData(self.snapFullPin, LOW)
        self.writeData(self.snapEmptyPin, HIGH)
        self.writeData(self.snapReadPin, LOW)

async def runGPIOTest(loop):
    gpioCtrl = GPIO_to_cRIO(qXmit=asyncio.Queue(maxsize=32),
                            inputPin=1,
                            clockPin=2,
                            latchPin=3,
                            clearPin=5,
                            outEnPin=6,
                            snapFullPin=13, 
                            snapEmptyPin=14, 
                            snapReadPin=15,
                            order=gpio.MSBFIRST,
                            clockTime=0
                            )
    
    testData = [(0b00000000, 0b00000001),
                (0b00001010, 0b00001011),
                (0b00010100, 0b00010101)]
    
    await gpioCtrl.qXmit.put(testData)
    await asyncio.gather(gpioCtrl.start())

if __name__ == "__main__":
    LOG_FORMAT = '%(asctime)s.%(msecs)03dZ %(name)-10s %(levelno)s \
        %(filename)s:%(lineno)d %(message)s'
    logging.basicConfig(datefmt = "%Y-%m-%d %H:%M:%S", format = LOG_FORMAT)
    logger = logging.getLogger('fodo')
    logger.setLevel(logging.DEBUG)
    logger.debug('~~~~~~starting log~~~~~~')

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(runGPIOTest(loop))
    except KeyboardInterrupt:
        print('Exiting Program...')
