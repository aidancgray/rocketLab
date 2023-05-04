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
        self.destIP = destinationIP
        self.destPort = destinationPort
        self.layer = layer
        self.pktHandler = packetHandler

    def start(self, bpf):
        sniff(filter=bpf, prn=lambda packet: self.handlePacket(packet))

    def handlePacket(self, pkt):
        self.logger.debug(f"PACKET: {pkt}")

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
    logger = logging.getLogger('fodo.packetanalyzer')
    logger.setLevel(logging.DEBUG)
    logger.info('~~~~~~starting log~~~~~~')

    srcIP = '172.16.0.171'
    srcPt = 1024
    dstIP = '172.16.1.112'
    dstPt = 1025
    lyr = 'udp'
    filter = f"src host {srcIP} and src port {srcPt} and dst host {dstIP} and dst port {dstPt} and {lyr}"
    #filter = f'{lyr}'
    
    pa = packetAnalyzer(srcIP,
                        srcPt,
                        dstIP,
                        dstPt,
                        lyr,
                        packetHandler=None
                        )

    pa.start(bpf=filter)
