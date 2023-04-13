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
# Shift out 123 (b1110110, byte 0-255) to data pin 1, clock pin 2 
#   wiringpi.shiftOut(1, 2, 0, 123)
###############################################################################

import wiringpi as gpio

LOW = 0
HIGH = 1
INPUT = 0
OUTPUT = 1

class shiftRegister:
    def __init__(self, id, inputPin, clockPin, clearPin, 
                 outputEnablePin, order, clockTime=0):
        self.id = id
        self.inpPin = inputPin
        self.clkPin = clockPin
        self.clrPin = clearPin
        self.oEnPin = outputEnablePin
        self.order = order
        self.clkTime = clockTime

        gpio.wiringPiSetupGpio()
        self.setupShiftPins()
        self.clearData()

    def tick(self):
        gpio.digitalWrite(self.clkPin, HIGH)
        gpio.delay(self.clkTime)
        gpio.digitalWrite(self.clkPin, LOW)
        gpio.delay(self.clkTime)

    def setupShiftPins(self):
        gpio.pinMode(self.inpPin, OUTPUT)
        gpio.pinMode(self.clkPin, OUTPUT)
        gpio.pinMode(self.clrPin, OUTPUT)
        gpio.pinMode(self.oEnPin, OUTPUT)

    def setData(self, data):
        gpio.shiftOut(self.inpPin, self.clkPin, self.order, data)

    def clearData(self):
        gpio.digitalWrite(self.clrPin, LOW)
        self.tick()
        gpio.digitalWrite(self.clrPin, HIGH)