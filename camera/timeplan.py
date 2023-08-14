"""
Functions to excute timeplan
"""

import datetime
import time
import sys
import os

def read_timeplan(file_plan):
    """
    Read the timeplan file in the format:
    YYYYMMDD\tHHMMSS\tHHMMSS\tHHMMSS\tseconds
    """
    plan = []
    with open(file_plan, 'r') as f:
        lines = f.readlines()
        for line in lines:
            # Skip the comment lines
            if line[0] == '#':
                continue
            # Skip the empty lines
            if line.strip() == '':
                continue
            # Parse the line
            line = line.strip()
            items = line.split('\t')
            if len(items) < 5:
                print('Error: The line "{}" is invalid!'.format(line))
                sys.exit(1)
            # Parse the start date and time
            start_date = items[0]
            # If the start date is '.', use the current date
            if start_date == '.':
                start_date = datetime.datetime.utcnow().strftime('%Y%m%d')
            start_time = items[1]
            start = datetime.datetime.strptime(start_date + start_time, '%Y%m%d%H%M%S')
            # Parse the end date and time
            end_date = items[2]
            # If the end date is '.', use the current date
            if end_date == '.':
                end_date = datetime.datetime.utcnow().strftime('%Y%m%d')
            end_time = items[3]
            end = datetime.datetime.strptime(end_date + end_time, '%Y%m%d%H%M%S')
            # Parse the interval
            interval = float(items[4])
            # Add the plan
            plan.append([start, end, interval])
    return plan
 

def timeplan(file_plan, func, test=False, sleep=1, **kwargs):
    plan = read_timeplan(file_plan)
    for item in plan:
        start = item[0]
        end = item[1]
        interval = item[2]
        while True:
            now = datetime.datetime.utcnow()

            # Check if the current time is in the plan
            if now >= start and now <= end:
                # check if it's in test mode
                if test:
                    # Print the current time in 'HH:MM:SSsss' format
                    print(now.strftime('%H:%M:%S.%f'), 'Trigger - Test', sep='\t')
                else:
                    # Print the current time
                    print(now.strftime('%H:%M:%S.%f'), 'Trigger', sep='\t')
                    # Execute the function
                    func(**kwargs)
                # Sleep for seconds
                time.sleep(interval)

            # If the current time is earlier than the start time, sleep for args.sleep seconds
            elif now < start:
                # Sleep for seconds
                time.sleep(sleep)
            else:
                # If the current time is later than the end time, exit
                break
