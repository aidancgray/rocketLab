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

class shiftRegister:
    def __init__(self, qXmit, inputPin, clockPin, latchPin, clearPin, 
                 outEnPin, order, clockTime=0):
        self.logger = logging.getLogger('fodo')
        self.qXmit = qXmit
        self.inputPin = inputPin
        self.clockPin = clockPin
        self.latchPin = latchPin
        self.clearPin = clearPin
        self.outEnPin = outEnPin
        self.order = order
        self.clockTime = clockTime

        gpio.wiringPiSetupGpio()
        self.setupShiftPins()
        self.clearData()

    async def start(self):
        while True:
            if not self.qXmit.empty():
                data = await self.qXmit.get()
                retData = await self.handleData(data)
            await asyncio.sleep(0.000001)

    async def handleData(self, data):
        for n in range(len(data)):
            #self.logger.debug(f"DATA[{n}]: {data[0]}")
            photon = data[n]
            x = photon[0]
            y = photon[1]
            p = photon[2]
            self.setData(y)
            await asyncio.sleep(0.000001)
            self.setData(x)
            await asyncio.sleep(0.000001)
            
    def tick(self):
        gpio.digitalWrite(self.clockPin, HIGH)
        gpio.delay(self.clockTime)
        gpio.digitalWrite(self.clockPin, LOW)
        gpio.delay(self.clockTime)

    def setPinMode(self, pin, mode):
        gpio.pinMode(pin, mode)

    def setupShiftPins(self):
        self.setPinMode(self.inputPin, OUTPUT)
        self.setPinMode(self.clockPin, OUTPUT)
        self.setPinMode(self.clearPin, OUTPUT)
        self.setPinMode(self.outEnPin, OUTPUT)

    def setData(self, data):
        gpio.shiftOut(self.inputPin, self.clockPin, self.order, data)

    def clearData(self):
        gpio.digitalWrite(self.clearPin, LOW)
        self.tick()
        gpio.digitalWrite(self.clearPin, HIGH)