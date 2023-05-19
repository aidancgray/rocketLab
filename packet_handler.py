#!/usr/bin/python3
# packet_handler.py
# 04/11/2023
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# Packet Handler class for JHU's Rocket Lab.
###############################################################################

import logging
import asyncio

class packetHandler:
    def __init__(self, qPacket, qXmit):
        self.logger = logging.getLogger('fodo')
        self.qPacket = qPacket
        self.qXmit = qXmit
        self.packetCount = 0

    async def start(self):
        while True:
            if not self.qPacket.empty():
                pkt = await self.qPacket.get()
                retData = await self.handlePacket(pkt)
                await self.enqueue_xmit(retData)
            await asyncio.sleep(0.000001)

    async def handlePacket(self, pkt):
        try:
            self.logger.debug(f'PACKET_SIZE: {len(pkt)}')
            if len(pkt) <= 62:
                self.logger.debug(f'PACKET: {pkt}')
            else:
                self.logger.debug(f'PACKET: {pkt[:62]} ... ')

            pktCount = (pkt[3]<<8) + pkt[2]

            # Make sure the data is aligned properly and is newest packet            
            if (pkt[4] == 0) and pkt[5] == 0 and (pktCount > self.packetCount):
                numPhotons = (pkt[1]<<8) + pkt[0]
                numPhotonBytes = numPhotons * 242
                
                self.logger.debug(f'NUM_PHOTONS: {numPhotons} ({numPhotonBytes}B)')
                
                # Split the packet into photons (X, Y, P) each consisting of 2 bytes
                pktData = pkt[6:]
                photonList = [pktData[i:i+6] for i in range(0, numPhotonBytes, 6)]
                
                if len(photonList) <= 10:
                    self.logger.debug(f'PHOTON_LIST: {photonList}')
                else:
                    self.logger.debug(f'PHOTON_LIST: {photonList[:10]} ... ')

                photonQueue = []
                pNum = 0
                for photon in photonList:
                    self.logger.debug(f'PHOTON[{pNum}]: {photon}')
                    x = (photon[1]<<3) + (photon[0]>>5)
                    y = (photon[3]<<3) + (photon[2]>>5)
                    # p = photon[4]
                    photonQueue.append((x, y))
                    pNum+=1
                    
                await self.enqueue_xmit(photonQueue)
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
    logger = logging.getLogger('fodo')
    logger.setLevel(logging.DEBUG)
    logger.debug('~~~~~~starting log~~~~~~')

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(runPktHandlerTest(loop))
    except KeyboardInterrupt:
        print('Exiting Program...')