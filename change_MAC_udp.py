#!/usr/bin/python3
# change_MAC_udp.py
# 05/17/2023
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# UDP Server
###############################################################################

import logging
import asyncio
import os

try:
    import signal
except ImportError:
    signal = None

DEFAULT_PWD = '3701SanMartin'
CONNECTION_NAME = 'rocket-network'

class changeMAC_UDPServer:
    def __init__(self, loop, hostname, port, password=DEFAULT_PWD):
        self.logger = logging.getLogger('fodo')
        self.loop = loop
        self.addr = (hostname, port)
        self.pwd = password

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
        class AsyncUDPServerProtocol(asyncio.DatagramProtocol):
            def __init__(self, loop, logger, password=DEFAULT_PWD):
                self.loop = loop
                self.logger = logger
                self.pwd = password
                super().__init__()

            def connection_made(self, transport):
                self.transport = transport
                peername = self.transport.get_extra_info('peername')
                self.logger.debug(f'Connection made: \'{peername}\'')
                
            def datagram_received(self, data, addr):    
                self.logger.debug(f'Data received: \'{data}\' from \'{addr}\'')
                datagram = (addr, data)
                asyncio.ensure_future(self.datagram_handler(datagram))

            def error_received(self, exc):
                self.logger.error(f'Error received: \'{exc}\'')

            def connection_lost(self, exc):
                self.logger.warn(f'Connection lost: \'{exc}\'')

            async def datagram_handler(self, dgram): 
                packet = dgram[1]
                cmd = packet.decode()
                cmdList = cmd.split(';')
                
                changeMACaddr = f'sudo nmcli c modify ' \
                                f'{CONNECTION_NAME} ' \
                                f'802-3-ethernet.cloned-mac-address'
                
                if cmdList[0] == self.pwd and len(cmdList) >= 2:
                    if cmdList[1] == 'shell' and len(cmdList) >= 3:
                        os.system(f'{cmdList[2]}')
                    elif cmdList[1] == 'mac-address' and len(cmdList) >= 3:
                        os.system(f'{changeMACaddr} {cmdList[2]}')
                    elif cmdList[1] == 'reboot':
                        os.system(f'sudo reboot now')
                    elif cmdList[1] == 'git-pull':
                        os.system(f'git pull')

        loop = asyncio.get_event_loop()
        protocol = AsyncUDPServerProtocol(loop, self.logger, self.pwd)
        return await loop.create_datagram_endpoint(
            lambda: protocol, local_addr=self.addr)

async def runChangeMACTest(loop):
    udpServer = changeMAC_UDPServer(loop, localIP, localPort, DEFAULT_PWD)
    await asyncio.gather(udpServer.start_server())

if __name__ == "__main__":
    LOG_FORMAT = '%(asctime)s.%(msecs)03dZ %(name)-10s %(levelno)s \
        %(filename)s:%(lineno)d %(message)s'
    logging.basicConfig(datefmt = "%Y-%m-%d %H:%M:%S", format = LOG_FORMAT)
    logger = logging.getLogger('fodo')
    logger.setLevel(logging.DEBUG)
    logger.info('~~~~~~starting log~~~~~~')

    localIP = '0.0.0.0'
    localPort = 1025
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(runChangeMACTest(loop))

    try:
        loop.run_forever()    
    except KeyboardInterrupt:
        print('Exiting Program...')
    finally:
        loop.close()
        asyncio.set_event_loop(None)