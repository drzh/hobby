"""
Trigger the camera from the Raspberry Pi

Usage:
    python trigger_from_pi.py -t <FILE_timeplan> -p <PIN> --test
"""

#!/usr/bin/python
import sys
import argparse
import time
import RPi.GPIO as GPIO
from timeplan import timeplan as timeplan

# Parse the arguments
parser = argparse.ArgumentParser(description='Trigger the camera from the Raspberry Pi')
parser.add_argument('-t', '--timeplan', help='Timeplan file', required=True)
parser.add_argument('-p', '--pin', help='GPIO pin', type=int, default=17)
parser.add_argument('--test', help='Test mode', action='store_true')
args = parser.parse_args()

# Function trigger()
def trigger(pin = 17, sleep_between = 0.02, sleep_after = 0.02):
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin,GPIO.HIGH)
    time.sleep(sleep_between)

    GPIO.output(pin,GPIO.OUT)
    GPIO.output(pin,GPIO.LOW)
    time.sleep(sleep_after)


# main()
def main():
    # Set the GPIO mode
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    timeplan(args.timeplan, func=trigger, test=args.test,  pin=args.pin, sleep_between=0.1, sleep_after=0.1)

# Call the main() function
if __name__ == '__main__':
    main()