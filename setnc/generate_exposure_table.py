"""
Generate exposure table for the SETnc.
Usage: python generate_exposure_table.py header.txt config.txt | <STDOUT>

header.txt: header of the exposure table
config.txt: configuration file for the exposure table in the following columns:
    start time: YYYY-MM-DD HH:MM:SS.S
    end time: YYYY-MM-DD HH:MM:SS.S
    interval: seconds
    exposure config: text in csv format
Output: exposure table in the csv format, and the 3rd column is replaced with the actural time in the format of YYYY-MM-DD HH:MM:SS.S
"""

import sys
import os
import datetime

def generate_exposure_table(header, config):
    with open(header, 'r') as f:
        lines = f.readlines()
        print(''.join(lines), end = '')

    with open(config, 'r') as f:
        for line in f:
            start, end, interval, exposure = line.strip().split('\t')
            start = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S.%f')
            end = datetime.datetime.strptime(end, '%Y-%m-%d %H:%M:%S.%f')
            interval = float(interval)
            exposure_list = exposure.split(',')
            # From start to end, generate the exposure config line for every interval seconds
            now = start
            while now <= end:
                exposure_list[2] = now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-5]
                print(','.join(exposure_list))
                now += datetime.timedelta(seconds=interval)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python generate_exposure_table.py header.txt config.txt | <STDOUT>')
        sys.exit(1)

    header = sys.argv[1]
    config = sys.argv[2]
    generate_exposure_table(header, config)