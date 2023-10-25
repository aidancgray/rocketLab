#!/usr/bin/python3
# packet_handler_bcast.py
# 10/03/2023
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# Packet Handler - Broadcast class for JHU's Rocket Lab.
###############################################################################

import logging
import asyncio
import socket
import struct
import subprocess
import time

SLEEP_TIME = 0.000001
ARPING_TIME = 5

class packetHandler:
    def __init__(self, qPacket, qXmit, bcastIP, bcastPort):
        self.logger = logging.getLogger('bcast')
        self.qPacket = qPacket
        self.qXmit = qXmit
        self.packetCount = 0
        self.bcastIP = bcastIP
        self.bcastPort = bcastPort
        
        if self.bcastIP[:3] == '192':
            self.srcIP = '192.168.1.10'
            self.localIP = '192.168.1.100'
        elif self.bcastIP[:3] == '172':
            self.srcIP = '172.16.0.171'
            self.localIP = '172.16.1.125'

    async def start(self):
        packet_timer = time.perf_counter()  # start a packet timer
        while True:
            if not self.qPacket.empty():
                pkt = await self.qPacket.get()
                retData = await self.handlePacket(pkt)
                if retData != None:
                    await self.enqueue_xmit(retData)
                packet_timer = time.perf_counter()  # reset packet timer
            else:
                packet_timer_check = time.perf_counter() - packet_timer
                if packet_timer_check > ARPING_TIME:  # check the packet timer
                    subprocess.run(["arping", "-U", 
                            "-c", "1",
                            "-I", "eth0",
                            "-s", self.localIP, 
                            self.srcIP], 
                            stdout=subprocess.PIPE)
                    await asyncio.sleep(2)

            await asyncio.sleep(SLEEP_TIME)

    async def handlePacket(self, pkt):
        try:
            rcv_time, addr, data = pkt
            
            if isinstance(data, bytes):
                udp_payload = data
            else:
                udp_payload = data.encode('utf-8')
                
            udp_header = struct.pack(">HHHH", 
                                     addr[1], 
                                     self.bcastPort, 
                                     8 + len(udp_payload), 
                                     0)
            ip_payload = udp_header + udp_payload

            ip_header = struct.pack(">BBH", 69, 0, 20 + len(ip_payload))
            ip_header += struct.pack(">HH", 12345, 0)
            ip_header += struct.pack(">BBH", 20, 17, 0)
            
            srcIP_split = addr[0].split('.')
            ip_header += struct.pack(">BBBB", 
                                     int(srcIP_split[0]),
                                     int(srcIP_split[1]),
                                     int(srcIP_split[2]),
                                     int(srcIP_split[3]))
            
            bcastIP_split = self.bcastIP.split('.')
            ip_header += struct.pack(">BBBB", 
                                     int(bcastIP_split[0]), 
                                     int(bcastIP_split[1]), 
                                     int(bcastIP_split[2]),
                                     int(bcastIP_split[3]))

            ip_pkt = ip_header + ip_payload

            sock = socket.socket(socket.AF_INET, 
                                 socket.SOCK_RAW, 
                                 socket.IPPROTO_RAW)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            
            self.logger.debug(f'Sending: \'{udp_payload}\'' \
                              f'to \'{(self.bcastIP, self.bcastPort)}\'' \
                              f'from \'{addr}\'')
            
            sock.sendto(ip_pkt, (self.bcastIP, self.bcastPort))
        except:
            pass

    async def enqueue_xmit(self, data):
        if self.qXmit.full():
            self.logger.warn(f'Transmit Data Queue is FULL')
        else:
            await self.qXmit.put(data)

async def runPktHandlerTest(loop):
    pktHandler = packetHandler(qPacket=asyncio.Queue(),
                               qXmit=asyncio.Queue()
                               )
    await asyncio.gather(pktHandler.start())

if __name__ == "__main__":
    LOG_FORMAT = '%(asctime)s.%(msecs)03dZ %(name)-10s %(levelno)s \
        %(filename)s:%(lineno)d %(message)s'
    logging.basicConfig(datefmt = "%Y-%m-%d %H:%M:%S", format = LOG_FORMAT)
    logger = logging.getLogger('bcast')
    logger.setLevel(logging.DEBUG)
    logger.debug('~~~~~~starting log~~~~~~')

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(runPktHandlerTest(loop))
    except KeyboardInterrupt:
        print('Exiting Program...')