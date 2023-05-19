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

try:
    import signal
except ImportError:
    signal = None

class AsyncUDPServer:
    def __init__(self, loop, hostname, port):
        self.logger = logging.getLogger('fodo')
        self.qPacket = asyncio.Queue(maxsize=32)
        self.qXmit = asyncio.Queue(maxsize=32)
        self.loop = loop
        self.addr = (hostname, port)
        self.serverTask = None

    def startUDP(self):
        if signal is not None:
            self.loop.add_signal_handler(signal.SIGINT, self.loop.stop)
        
        transport, server = self.start_server()
        
        try:
            self.loop.run_forever()
        finally:
            server.close()
            self.loop.close()

    async def start_server(self):
        print('DEBUG1')
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
                if self.qPacket.full():
                    self.logger.warn(f'Incoming Packet Queue is full')
                else:
                    await self.qPacket.put(packet)

        loop = asyncio.get_event_loop()
        protocol = AsyncUDPServerProtocol(loop, self.logger, self.qPacket)
        return await loop.create_datagram_endpoint(
            lambda: protocol, local_addr=self.addr)
        #transport, server = self.loop.run_until_complete(serverTask)
        #return transport, server

async def runUDPserverTest(loop):
    udpServer = AsyncUDPServer(loop, localIP, localPort)
    await asyncio.gather(udpServer.start_server())

if __name__ == "__main__":
    LOG_FORMAT = '%(asctime)s.%(msecs)03dZ %(name)-10s %(levelno)s \
        %(filename)s:%(lineno)d %(message)s'
    logging.basicConfig(datefmt = "%Y-%m-%d %H:%M:%S", format = LOG_FORMAT)
    logger = logging.getLogger('fodo')
    logger.setLevel(logging.DEBUG)
    logger.debug('~~~~~~starting log~~~~~~')

    localIP = '172.16.1.125'
    localPort = 1025
    # localIP = '192.168.1.100'
    # localPort = 60000
    # srcIP = '172.16.1.112'
    # srcPort = 1025
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(runUDPserverTest(loop))

    try:
        loop.run_forever()    
    except KeyboardInterrupt:
        print('Exiting Program...')
    finally:
        loop.close()
        asyncio.set_event_loop(None)