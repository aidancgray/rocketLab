#!/usr/bin/python3.6
# main.py
# 04/04/2023
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# Main script for running the First Order Data Out (FODO) 
# for JHU's Rocket Lab.
###############################################################################

import sys
import asyncio
import netifaces
import logging
import argparse
import configparser
import shlex
import wiringpi as gpio

from shift_register import shiftRegister
from packet_analyzer import packetAnalyzer
from packet_handler import packetHandler

#      IDX |  0    1    2    3    4    5    6    7    8    9   10   11   12
#     PHYS |  6    7    8   15   16   29   30   31   32   33   35   37   39
PIN_LIST = [470, 471, 472, 506, 505, 423, 422, 425, 424, 507, 477, 421, 462]

SHIFTREG_INPUT_PIN = PIN_LIST[0]
SHIFTREG_CLOCK_PIN = PIN_LIST[1]
SHIFTREG_LATCH_PIN = PIN_LIST[2]
SHIFTREG_CLEAR_PIN = PIN_LIST[3]
SHIFTREG_OUTEN_PIN = PIN_LIST[4]

SNAP_FIFO_FULL_PIN = PIN_LIST[5]
SNAP_FIFO_EMPTY_PIN = PIN_LIST[6]
SNAP_FIFO_READ_PIN = PIN_LIST[7]

DELAY = 2000

DEFAULT_CONFIG = {
    "SOURCE_IP" : "172.16.1.112",
    "SOURCE_PORT" : 1025,
    "DESTINATION_IP" : "172.16.1.34",
    "DESTINATION_PORT" : 1025,
    "NETWORK_LAYER" : "udp"}

def custom_except_hook(loop, context):
    if repr(context['exception']) == 'SystemExit()':
        print('Exiting Program...')

async def runFODO(opts):
    logging.basicConfig(datefmt = "%Y-%m-%d %H:%M:%S",
                        format = '%(asctime)s.%(msecs)03dZ ' \
                                '%(name)-10s %(levelno)s ' \
                                '%(filename)s:%(lineno)d %(message)s')
    
    logger = logging.getLogger('fodo')
    logger.setLevel(opts.logLevel)
    logger.info('~~~~~~starting log~~~~~~')

    if opts.test:
        gpioTest()
        sys.exit()
    
    if opts.config == None:
        config = DEFAULT_CONFIG
    else:
        config = parseConfigFile(opts.config)

    srcIP = config["SOURCE_IP"]
    srcPort = config["SOURCE_PORT"]
    dstIP = config["DESTINATION_IP"]
    dstPort = config["DESINATion_PORT"]
    layer = config["NETWORK_LAYER"]

    bpf_filter = f"src host {srcIP} and " \
        f"src port {srcPort} and " \
        f"dst host {dstIP} and " \
        f"dst port {dstPort} and " \
        f"{layer}"
    
    ip_address = netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['addr']
    

    shiftReg = shiftRegister(inputPin=SHIFTREG_INPUT_PIN,
                             clockPin=SHIFTREG_CLOCK_PIN,
                             latchPin=SHIFTREG_LATCH_PIN,
                             clearPin=SHIFTREG_CLEAR_PIN,
                             outEnPin=SHIFTREG_OUTEN_PIN,
                             order=gpio.LSBFIRST,
                             clockTime=opts.tickRate
                            )
    
    pktHandler = packetHandler(customHandler=shiftReg)
    
    pktAnalyzer = packetAnalyzer(sourceIP=srcIP,
                                  sourcePort=srcPort,
                                  destinationIP=dstIP,
                                  destinationPort=dstPort,
                                  layer=layer,
                                  packetHandler=pktHandler
                                  )

    pktAnalyzer.start(bpf_filter)

def gpioTest():
    gpio.wiringPiSetupGpio()
    print("---GPIO Test---")
    
    print(f'#ofPINS...{str(len(PIN_LIST))}')
    for pin in PIN_LIST:
        gpio.pinMode(pin, gpio.OUTPUT)
        gpio.digitalWrite(pin, gpio.LOW)
    gpio.delay(DELAY)
    print("PINS LOW")
    for pin in PIN_LIST:
        readVal = gpio.digitalRead(pin)
        print(f'{str(pin)}...{str(readVal)}')
    
    for pin in PIN_LIST:
        gpio.digitalWrite(pin, gpio.HIGH)
    gpio.delay(DELAY)
    print("PINS HIGH")
    for pin in PIN_LIST:
        readVal = gpio.digitalRead(pin)
        print(f'{str(pin)}...{str(readVal)}')

    for pin in PIN_LIST:
        gpio.digitalWrite(pin, gpio.LOW)
    print("---DONE---")

def parseConfigFile(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    filterInfo = {}
    filterInfo['SOURCE_IP'] = config['FILTER INFO']['SOURCE IP']
    filterInfo['SOURCE_PORT'] = config['FILTER INFO']['SOURCE PORT']
    filterInfo['DESTINATION_IP'] = config['FILTER INFO']['DESTINATION IP']
    filterInfo['DESTINATION_PORT'] = config['FILTER INFO']['DESTINATION PORT']
    filterInfo['NETWORK_LAYER'] = config['FILTER INFO']['NETWORK LAYER']

    return filterInfo
    
def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if isinstance(argv, str):
        argv = shlex.split(argv)

    parser = argparse.ArgumentParser(sys.argv[0])
    parser.add_argument('--config', type=str, default=None,
                        help='name of the config file, ex: config.ini')
    parser.add_argument('--logLevel', type=int, default=logging.INFO,
                        help='logging threshold. 10=debug, 20=info, 30=warn')
    parser.add_argument('--test', type=bool, default=False,
                        help='run in test mode')
    parser.add_argument('--delay', type=int, default=2000,
                        help='in milliseconds - used for pausing')
    parser.add_argument('--tickRate', type=int, default=0,
                        help='in milliseconds - clock tick rate')

    opts = parser.parse_args(argv)
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(custom_except_hook)
    try:
        #runFODO(opts)
        loop.run_until_complete(runFODO(opts))
    except KeyboardInterrupt:
        print('Exiting Program...')
    
if __name__ == "__main__":
    main()
    
