#!/usr/bin/python3
# packet_analyzer.py
# 04/11/2023
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# Packet Analyzer class for JHU's Rocket Lab.
###############################################################################

import logging
import warnings

with warnings.catch_warnings():
	warnings.filterwarnings("ignore")
	from scapy.all import *

class packetAnalyzer:
    def __init__(self, 
                 sourceIP, sourcePort, 
                 destinationIP, destinationPort, 
                 layer, packetHandler):
        self.logger = logging.getLogger('fodo.packet_analyzer')
        self.srcIP = sourceIP
        self.srcPort = sourcePort
        self.dstIP = destinationIP
        self.dstPort = destinationPort
        self.layer = layer
        self.pktHandler = packetHandler

        self.filter = f"src host {self.srcIP} and " \
                      f"src port {self.srcPort} and " \
                      f"dst host {self.dstIP} and " \
                      f"dst port {self.dstPort} and " \
                      f"{self.layer}"

    def start(self, bpf=None):
        if bpf == None:
                sniff(filter=self.filter, prn=lambda packet: self.handlePacket(packet))
        else:
                sniff(filter=bpf, prn=lambda packet: self.handlePacket(packet))

    def handlePacket(self, pkt):
        self.logger.debug(f'PACKET: {pkt}')
                          
        if self.pktHandler == None:
                try:
                        self.handlePacketLoad(pkt.load)
                except:
                        pass
        else:
                self.pktHandler.handle(pkt)

    def handlePacketLoad(self, pktLoad):
        self.logger.info(f"PACKET_LOAD: {pktLoad}")

if __name__ == "__main__":
    LOG_FORMAT = '%(asctime)s.%(msecs)03dZ %(name)-10s %(levelno)s \
        %(filename)s:%(lineno)d %(message)s'
    logging.basicConfig(datefmt = "%Y-%m-%d %H:%M:%S", format = LOG_FORMAT)
    logger = logging.getLogger('fodo.packet_analyzer')
    logger.setLevel(logging.DEBUG)
    logger.info('~~~~~~starting log~~~~~~')

    srcIP = '172.16.1.112'
    srcPort = 1025
    dstIP = '172.16.1.34'
    dstPort = 1025
    layer = 'udp'

    #filter = f"host {srcIP} and host {dstIP} and port {dstPort} and {layer}"
    filter = f"src host {srcIP} and " \
        f"src port {srcPort} and " \
        f"dst host {dstIP} and " \
        f"dst port {dstPort} and " \
        f"{layer}"
    
    pa = packetAnalyzer(srcIP,
                        srcPort,
                        dstIP,
                        dstPort,
                        layer,
                        packetHandler=None
                        )

    pa.start(bpf=filter)
