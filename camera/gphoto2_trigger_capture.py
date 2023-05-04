# Usage: Trigger capture accroding to the time schedule given by the input file
# Usage: python3 trigger_capture.py -i <input file>
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
import gphoto2 as gp

# Parse the arguments
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', dest = 'input', help = 'Input file')
args = parser.parse_args()

# Trigger one time
def trigger_onetime():
    # print the current time in UTC
    print('{}'.format(datetime.datetime.utcnow().strftime('%Y%m%d %H:%M:%S')), end = '')
    # Trigger the capture
    print(' : Trigger the capture', end = '')
    cmd = 'gphoto2 --trigger-capture'
    os.system(cmd)
    #print(cmd)
    #camera.trigger_capture()
    print()
 
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
def trigger_plan(plan):
    #camera = gp.Camera()
    # Start the capture
    while True :
        # Get the current time
        now = datetime.datetime.utcnow()
        # Check if the current time is in the plan
        for item in plan :
            start = item[0]
            end = item[1]
            interval = item[2]
            if now >= start and now <= end :
                # Trigger the capture
                trigger_onetime()
                # Sleep for the interval
                time.sleep(interval)
                break
        # If the current time is not in the plan, exit
        #if now < item[0] or now > item[1] :
        #    break

# Main function
def main():
    # Read the input file
    plan = read_input_file(args.input)
    # Trigger according to the time schedule
    trigger_plan(plan)

if __name__ == '__main__':
    main()
