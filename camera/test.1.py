# Use bluez to triger the shutter release of canon 200D
# Usage: prog -b <bluetooth address>

import sys
#import bluetooth
import time
import argparse
from subprocess import Popen, PIPE

# Parse the arguments
parser = argparse.ArgumentParser(description='Use bluez to triger the shutter release of canon 200D')
parser.add_argument('-b', '--bluetooth', help='The bluetooth address of the camera', required=True)
args = parser.parse_args()

# The bluetooth address of the camera
camera = args.bluetooth

DEVICE_NAME = "PY"

BUTTON_RELEASE = 0b10000000
BUTTON_FOCUS   = 0b01000000
BUTTON_TELE    = 0b00100000
BUTTON_WIDE    = 0b00010000
MODE_IMMEDIATE = 0b00001100
MODE_DELAY     = 0b00000100
MODE_MOVIE     = 0b00001000

p = Popen('btgatt-client -d ' + camera + ' -t random -I', stdin=PIPE, stdout=PIPE, universal_newlines=True, shell=True)

def wait_contain(s):
    while True:
        line = p.stdout.readline()
        if s in line:
            break

def write_value(*values):
    p.stdin.write("write-value " + ' '.join(map(str, values)) + '\n')
    p.stdin.flush()
    wait_contain("Write successful")

wait_contain("GATT discovery procedures complete")
write_value(0xf504, 3, *map(ord, DEVICE_NAME))

if cmd != 'pair':
    button = BUTTON_RELEASE
    mode = MODE_IMMEDIATE
    write_value(0xf506, button | mode)