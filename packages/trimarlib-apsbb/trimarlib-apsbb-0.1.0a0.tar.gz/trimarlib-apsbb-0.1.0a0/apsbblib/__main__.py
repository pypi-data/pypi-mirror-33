import argparse
import logging
import erpc
import time
import os
import signal
import threading

LOG_FMT = '%(levelname)s %(module)s:%(threadName)s:%(funcName)s %(message)s'
logging.basicConfig(format=LOG_FMT)
LOGGER = logging.getLogger('.'.join(['apsbblib', __name__]))
CANCEL = threading.Event()

from .server import Server
from .version import VERSION


def sig_handler(signum, frame):
    LOGGER.info('signal handler called: %s', signum)
    CANCEL.set()

signal.signal(signal.SIGTERM, sig_handler)

parser = argparse.ArgumentParser(
    prog='apsbblib',
    description='Run APSBackBone IPC server')
parser.add_argument(
    '-p', '--port',
    type=str,
    default='/dev/ttyS1',
    help='''\
serial port to be used as communication channel with the backbone hardware''')
parser.add_argument(
    '-b', '--baudrate',
    type=int,
    default=115200,
    help='''\
baudrate of the serial port towards the backbone hardware''')
parser.add_argument(
    '-v', '--verbose',
    action='count',
    help='''\
increase program verbosity''')
parser.add_argument(
    '--firmware',
    type=str,
    help='''\
path to the firmware to be verified and uploaded to the backbone hardware''')
parser.add_argument(
    '-V', '--version',
    action='version',
    version=VERSION)
ns = parser.parse_args()

if ns.verbose == None:
    LOGGER.setLevel(logging.WARNING)
elif ns.verbose == 1:
    LOGGER.setLevel(logging.INFO)
else:
    LOGGER.setLevel(logging.DEBUG)

SERVER = Server(port=ns.port, baudrate=ns.baudrate, firmware=ns.firmware)
try:
    SERVER.start()
except:
    LOGGER.exception('failed to start APSBackBone IPC server')
    exit(1)

LOGGER.info('APSBackBone IPC server started.')
try:
    CANCEL.wait()
except KeyboardInterrupt:
    pass
LOGGER.info('shutting down APSBackBone IPC server.')

SERVER.stop()
