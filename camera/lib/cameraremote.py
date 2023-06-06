"""
This module provides the library functions for the camera remote control.
"""

import datetime

"""
    Function read_plan reads the time plan from the input file.
    The input file should be a TSV file with the following columns (Time is in UTC):
        1. The start date in the format of YYYYMMDD
        2. The start time in the format of HHMMSS
        3. The end date in the format of YYYYMMDD
        4. The end time in the format of HHMMSS
        5. The interval between two captures in seconds (can be a float)

    Parameters:
        file: The input file
"""
def read_plan(file):
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
 