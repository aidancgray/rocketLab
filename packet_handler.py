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

    async def start(self):
        while True:
            if not self.qPacket.empty():
                pkt = await self.qPacket.get()
                retData = await self.handlePacket(pkt)
                await self.enqueue_xmit(retData)
            await asyncio.sleep(0.000001)

    async def handlePacket(self, pkt):
        self.logger.debug(f"PACKET: {pkt}")
        # parse out the packet contents