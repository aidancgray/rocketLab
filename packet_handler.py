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
    def __init__(self, customHandler):
        self.logger = logging.getLogger('fodo.packet_handler')
        self.handler = customHandler

    def handle(self, pkt):
        self.logger.debug(f"PACKET: {pkt}")
        self.handlePacketLoad(pkt.load)

    def handlePacketLoad(self, pktLoad):
        self.logger.debug(f"PACKET LOAD: {pktLoad}")
        #self.handler.setData(pktLoad)