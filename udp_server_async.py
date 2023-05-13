#!/usr/bin/python3
# udp_server.py
# 05/09/2023
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# UDP Server
###############################################################################

import logging
import asyncio
import sys

try:
    import signal
except ImportError:
    signal = None

class AsyncUDPServer:
    def __init__(self, loop, hostname, port):
        self.logger = logging.getLogger('fodo')
        self.qPacket = asyncio.Queue()
        self.qXmit = asyncio.Queue()
        self.loop = loop
        self.addr = (hostname, port)

    def startUDP(self):
        if signal is not None:
            self.loop.add_signal_handler(signal.SIGINT, self.loop.stop)
        
        server = self.start_server()

        try:
            self.loop.run_forever()
        finally:
            server.close()
            self.loop.close()

    def start_server(self):
        class AsyncUDPServerProtocol(asyncio.DatagramProtocol):
            def __init__(self, loop, logger, qPacket):
                self.loop = loop
                self.logger = logger
                self.qPacket = qPacket
                super().__init__()

            def connection_made(self, transport):
                self.transport = transport
                peername = self.transport.get_extra_info('peername')
                self.logger.debug(f'Connection made: \'{peername}\'')
                
            def datagram_received(self, data, addr):    
                self.logger.debug(f'Data received: \'{data}\' from \'{addr}\'')
                #self.transport.sendto(data, addr)
                datagram = (addr, data)
                asyncio.ensure_future(self.datagram_handler(datagram))

            def error_received(self, exc):
                self.logger.error(f'Error received: \'{exc}\'')

            def connection_lost(self, exc):
                self.logger.warn(f'Connection lost: \'{exc}\'')

            async def datagram_handler(self, dgram): 
                packet = dgram[1]
                self.loop.create_task(self.enqueue_packet(packet))

            async def enqueue_packet(self, packet):
                await self.qPacket.put(packet)

        protocol = AsyncUDPServerProtocol(self.loop, self.logger, self.qPacket)
        t = asyncio.Task(self.loop.create_datagram_endpoint(
            lambda: protocol, local_addr=self.addr
            ))
        transport, server = self.loop.run_until_complete(t)
        return transport

if __name__ == "__main__":
    LOG_FORMAT = '%(asctime)s.%(msecs)03dZ %(name)-10s %(levelno)s \
        %(filename)s:%(lineno)d %(message)s'
    logging.basicConfig(datefmt = "%Y-%m-%d %H:%M:%S", format = LOG_FORMAT)
    logger = logging.getLogger('fodo')
    logger.setLevel(logging.DEBUG)
    logger.info('~~~~~~starting log~~~~~~')

    #localIP = '172.16.1.34'
    #local{prt = 1025
    localIP = '192.168.1.100'
    localPort = 60000
    srcIP = '172.16.1.112'
    srcPort = 1025
    
    loop = asyncio.get_event_loop()

    udpServer = AsyncUDPServer(loop, localIP, localPort)
    udpServer.startUDP()
