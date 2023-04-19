#!/usr/bin/python3
# packet_sniffer.py
# 04/11/2023
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# Packet Sniffer class for JHU's Rocket Lab.
###############################################################################

import logging
import asyncio
from scapy.all import *

class packetSniffer:
    def __init__(self, sourceIP, destinationIP, destinationPort):
        self.logger = logging.getLogger('fodo')
        self.srcIP = sourceIP
        self.destIP = destinationIP
        self.destPort = destinationPort
        
        self.qRecv = asyncio.Queue()
        self.qXmit = asyncio.Queue()
        self.startup()

    def startup(self):
        pass