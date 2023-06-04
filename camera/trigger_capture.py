# Usage: Trigger capture accroding to the time schedule given by the input file
# Usage: python3 trigger_capture.py -i <input file> -b <bluetooth address> -t <Binary_test> -s <sleep time before the starting time>
#       The input file should be a TSV file with the following columns (Time is in UTC):
#       1. The start date in the format of YYYYMMDD
#       2. The start time in the format of HHMMSS
#       3. The end date in the format of YYYYMMDD
#       4. The end time in the format of HHMMSS
#       5. The interval between two captures in seconds (can be a float)

import argparse
import datetime
import time
import sys
import os
import asyncio
import subprocess
from canoremote import CanoRemote, Button, Mode

# Parse the arguments
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', dest = 'input', help = 'Input file')
parser.add_argument('-b', '--bluetooth', dest = 'bluetooth', help = 'Bluetooth address')
parser.add_argument('-t', '--test', dest = 'test', help = 'Binary test', type=bool, default=False, action=argparse.BooleanOptionalAction)
parser.add_argument('-s', '--sleep', dest = 'sleep', help = 'Sleep time before the starting time', type=float, default=0.01)
args = parser.parse_args()

# Read the input file
def read_input_file(file):
    plan = []
    with open(file, 'r') as f :
        lines = f.readlines()
        for line in lines :
            # Skip the comment lines
            if line[0] == '#' :
                continue
            # Skip the empty lines
            if line.strip() == '' :
                continue
            # Parse the line
            line = line.strip()
            items = line.split('\t')
            if len(items) < 5 :
                print('Error: The line "{}" is invalid!'.format(line))
                sys.exit(1)
            # Parse the start date and time
            start_date = items[0]
            # If the start date is '.', use the current date
            if start_date == '.' :
                start_date = datetime.datetime.utcnow().strftime('%Y%m%d')
            start_time = items[1]
            start = datetime.datetime.strptime(start_date + start_time, '%Y%m%d%H%M%S')
            # Parse the end date and time
            end_date = items[2]
            # If the end date is '.', use the current date
            if end_date == '.' :
                end_date = datetime.datetime.utcnow().strftime('%Y%m%d')
            end_time = items[3]
            end = datetime.datetime.strptime(end_date + end_time, '%Y%m%d%H%M%S')
            # Parse the interval
            interval = float(items[4])
            # Add the plan
            plan.append([start, end, interval])
    return plan

# Trigger according to the time schedule
async def trigger_plan(plan, addr):
    MODE=Mode.Immediate
    async with CanoRemote(addr, timeout=5) as cr:
        print("Initialize ...")
        await cr.initialize()
        print('Connected:', cr.is_connected)

        # Wait for 0.05 seconds
        await asyncio.sleep(0.05)
    
        for item in plan :
            start = item[0]
            end = item[1]
            interval = item[2]
            while True :
                # Get the current time
                now = datetime.datetime.utcnow()
                #print("Current time: ", now.strftime('%Y %m %H:%M:%S'))

                # Check if the current time is in the plan
                if now >= start and now <= end :
                    # check if it's in test mode
                    if args.test:
                        # Print the current time in 'HH:MM:SSsss' format
                        print(now.strftime('%H:%M:%S.%f'), 'Trigger - Test', sep='\t')
                    else:
                        # Print the current time
                        print(now.strftime('%H:%M:%S.%f'), 'Trigger', sep='\t')
                        # Trigger the capture
                        await cr.state(MODE, Button.Release)
                        await cr.state(MODE)
                    # Sleep for the interval
                    await asyncio.sleep(interval)

                # If the current time is earlier than the start time, sleep for args.sleep seconds
                elif now < start :
                    # Sleep for args.sleep seconds
                    await asyncio.sleep(args.sleep)
                else :
                    # If the current time is later than the end time, exit
                    break  

            ## If the current time is later than the end time of the last item in the plan, exit
            #if now > plan[-1][1] :
                #break

# Main function
def main():
    # Read the input file
    plan = read_input_file(args.input)
    # Trigger according to the time schedule
    loop = asyncio.get_event_loop()
    loop.run_until_complete(trigger_plan(plan, args.bluetooth))

if __name__ == '__main__':
    main()
