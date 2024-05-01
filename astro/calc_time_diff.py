'''
Calculate the difference between two time strings

Usage: calc_time_diff.py -i <input_file> -o <output_file> -t1 <column_time1> -t2 <column_time2>
'''

import sys
import click
import numpy as np
from astropy.time import Time
from datetime import datetime, timedelta

def calc_time_diff(input_file, output_file, column_time1, column_time2):
    column_time1 -= 1
    column_time2 -= 1
    with open(input_file, 'r') as f:
        for line in f:
            line = line.rstrip()
            data = line.split('\t')
            #t1 = Time(data[column_time1])
            t1_date, t1_fraction = data[column_time1].split('.')
            t1_date_fmt = datetime.strptime(t1_date, '%Y-%m-%d')
            t1_hour_fmt = int(t1_fraction) * 24 / 10
            t1 = t1_date_fmt + timedelta(hours=t1_hour_fmt)
            t2 = datetime.strptime(data[column_time2], '%Y-%m-%d %H:%M:%S.%f')
            time_diff = datetime(t2.year, t2.month, t2.day, t2.hour, t2.minute, t2.second) - datetime(t1.year, t1.month, t1.day, t1.hour, t1.minute, t1.second)
            time_diff_in_seconds = time_diff.total_seconds()
            print(line, time_diff_in_seconds, sep='\t')

@click.command()
@click.option('-i', '--input_file', type=click.Path(exists=True), help='Input tsv file containing the time strings', default='/dev/stdin')
@click.option('-o', '--output_file', type=click.Path(), help='Output tsv file containing the time difference', default='/dev/stdout')
@click.option('-t1', '--column_time1', type=int, help='Column number of the first time string', default=2)
@click.option('-t2', '--column_time2', type=int, help='Column number of the second time string', default=10)

def main(input_file, output_file, column_time1, column_time2):
    calc_time_diff(input_file, output_file, column_time1, column_time2)

if __name__ == '__main__':
    main()
