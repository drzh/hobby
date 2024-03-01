"""
Trigger the camera from the Raspberry Pi

Usage:
    python trigger_from_pi.py -t <FILE_timeplan> -p <PIN> -b <sleep_between> --test
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
#parser.add_argument('-b', '--sleep_between', help='Sleep between', type=float, default=0.02)
#parser.add_argument('-a', '--sleep_after', help='Sleep after', type=float, default=0.02)
parser.add_argument('--test', help='Test mode', action='store_true')
args = parser.parse_args()

# Function trigger()
def trigger(pin = 17, duration = 0.02):
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin,GPIO.HIGH)
    time.sleep(duration)

    GPIO.output(pin,GPIO.OUT)
    GPIO.output(pin,GPIO.LOW)

# main()
def main():
    # Set the GPIO mode
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    timeplan(args.timeplan, func=trigger, test=args.test,  pin=args.pin, sleep_between=args.sleep_between)

    # Clean up
    GPIO.cleanup()

# Call the main() function
if __name__ == '__main__':
    main()