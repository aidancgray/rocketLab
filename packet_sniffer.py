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
import queue
from scapy.all import *

class packetSniffer:
    def __init__(self, sourceIP, destinationIP, destinationPort, layer):
        self.logger = logging.getLogger('fodo')
        self.srcIP = sourceIP
        self.destIP = destinationIP
        self.destPort = destinationPort
        self.layer = layer
        
        self.qRecv = asyncio.Queue()
        self.qXmit = asyncio.Queue()

    async def start(self):
        sniff(filter=f"src host {self.srcIP} and port {self.destPort} and {self.layer}",
              prn=lambda packet: self.queuePacketLoad(packet.load))
        
    def queuePacketLoad(self, pktLoad):
        self.qRecv.put(pktLoad)