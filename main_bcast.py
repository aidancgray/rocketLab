#!/usr/bin/python3.6
# main_bcast.py
# 10/03/2023
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# Main script for running the data broadcast
# for JHU's Rocket Lab.
###############################################################################

import sys
import os
import asyncio
import netifaces
import logging
import argparse
import shlex

from udp_server_async_bcast import AsyncUDPServer
from packet_handler_bcast import packetHandler

DELAY = 2000
IP_ANN_DELAY = 5 #seconds

def custom_except_hook(loop, context):
    logger = logging.getLogger('bcast')
    logger.setLevel(logging.WARN)
    
    if repr(context['exception']) == 'SystemExit()':
        logger.debug('Exiting Program...')

async def runBCAST(loop, opts):
    logging.basicConfig(datefmt = "%Y-%m-%d %H:%M:%S",
                        format = '%(asctime)s.%(msecs)03dZ ' \
                                 '%(name)-10s %(levelno)s ' \
                                 '%(filename)s:%(lineno)d %(message)s')
    
    logger = logging.getLogger('bcast')
    logger.setLevel(opts.logLevel)
    logger.info('~~~~~~starting log~~~~~~')

    try:
        localIP = netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['addr']
    except:
        localIP = '192.168.1.100'
    
    if localIP[:3] == '192':
        bcastIP = "192.168.1.255"
    elif localIP[:3] == '172':
        bcastIP = "172.16.15.255"
    
    bcastPort = 60000

    logger.info(f'VIM-BCAST_IP_ADDRESS={localIP}')
    logger.info(f'UDP_BROADCAST_ADDRESS={bcastIP}')
    logger.info(f'BROADCAST_PORT={bcastPort}')

    udpServer = AsyncUDPServer(loop, localIP, bcastPort)
    pktHandler = packetHandler(qPacket=udpServer.qPacket,
                               qXmit=udpServer.qXmit,
                               bcastIP=bcastIP,
                               bcastPort=bcastPort)
    
    ipAnnTask = loop.create_task(ipAnnounce)

    await asyncio.gather(udpServer.start_server(), 
                         pktHandler.start(),
                         ipAnnounce(),
                         )
    
async def ipAnnounce():
    while True:
        #os.system("arping -A -c 1 -I eth0 192.168.1.100")
        os.system("ping -c 1 192.168.1.10")
        await asyncio.sleep(IP_ANN_DELAY)

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if isinstance(argv, str):
        argv = shlex.split(argv)

    parser = argparse.ArgumentParser(sys.argv[0])
    parser.add_argument('--logLevel', type=int, default=logging.INFO,
                        help='logging threshold. 10=debug, 20=info, 30=warn')

    opts = parser.parse_args(argv)
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(custom_except_hook)
    loop.run_until_complete(runBCAST(loop, opts))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print('Exiting Program...')
    finally:
        loop.close()
        asyncio.set_event_loop(None)
    
if __name__ == "__main__":
    main()
    
