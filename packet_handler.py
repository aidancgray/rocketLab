#!/usr/bin/python3
# packet_handler.py
# 04/11/2023
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# Packet Handler class for JHU's Rocket Lab.
###############################################################################

import logging
from scapy.all import *

class packetHandler:
    def __init__(self, logger, customHandler):
        self.logger = logger
        self.handler = customHandler

    def handle(self, pkt):
        self.logger.info(f"PACKET: {pkt}")