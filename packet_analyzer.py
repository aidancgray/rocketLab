#!/usr/bin/python3
# packet_analyzer.py
# 04/11/2023
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# Packet Analyzer class for JHU's Rocket Lab.
###############################################################################

import logging
from scapy.all import *

class packetAnalyzer:
    def __init__(self, 
                 sourceIP, sourcePort, 
                 destinationIP, destinationPort, 
                 layer, packetHandler):
        self.logger = logging.getLogger('fodo.packet_analyzer')
        self.srcIP = sourceIP
        self.srcPort = sourcePort
        self.destIP = destinationIP
        self.destPort = destinationPort
        self.layer = layer
        self.pktHandler = packetHandler

    def start(self, bpf):
        sniff(filter=bpf, prn=lambda packet: self.handlePacket(packet))
                
    def handlePacket(self, pkt):
        self.logger.debug(f"PACKET: {pkt}")
        self.handlePacketLoad(pkt.load)
        self.pktHandler.handle(pkt)

    def handlePacketLoad(self, pktLoad):
        self.logger.debug(f"PACKET_LOAD: {pktLoad}")
        