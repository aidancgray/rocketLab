#!/usr/bin/python3
# gpio.py
# 04/10/2023
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# GPIO class. 
###############################################################################

import wiringpi as gpio

class GPIO:
    def __init__(self, pinList):
        self.pinList = pinList