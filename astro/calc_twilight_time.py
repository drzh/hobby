'''
Calculat the sunrise, sunset and twilight times for a given location and date.

Usage: python calc_twilight_time.py --lat <latitude> --lon <longitude> --dstart <start date> --dend <end date> --tz <time zone> -o <output file>

'''

import sys
import click
import ephem
from datetime import datetime
from pytz import timezone

@click.command()
@click.option('--lat', help='Latitude of the location', type=float, default=32.8)
@click.option('--lon', help='Longitude of the location', type=float, default=-96.8)
@click.option('--dstart', help='Start date', type=str, default='2024-08-18')
@click.option('--dend', help='End date', type=str, default='2024-08-18')
@click.option('--tz', help='Time zone', type=str, default='America/Chicago')
@click.option('-o', '--output', help='Output file', type=str, default='/dev/stdout')

def calc_twilight_time(lat, lon, dstart, dend, tz, output):
    tzone = tz
    tfmt = "%Y-%m-%d %H:%M:%S"
    dstart = datetime.strptime(dstart, '%Y-%m-%d').replace(tzinfo=timezone(tzone)).astimezone(timezone('UTC')).strftime('%Y-%m-%d %H:%M:%S')
    dend = datetime.strptime(dend, '%Y-%m-%d').replace(tzinfo=timezone(tzone)).astimezone(timezone('UTC')).strftime('%Y-%m-%d %H:%M:%S')
    
    observer = ephem.Observer()
    observer.lat = str(lat)
    observer.lon = str(lon)
    observer.elevation = 0
    observer.horizon = '0'
    observer.pressure = 0
    observer.temp = 0
    observer.date = dstart

    with open(output, 'w') as f:
        # Print parameters
        print("# latitude=", lat, "; longitude=", lon, "; timezone=", tzone, sep='', file=f)
        while observer.date.datetime().strftime('%Y-%m-%d %H:%M:%S') <= dend:
            observer.horizon = '0'
            sunrise = observer.next_rising(ephem.Sun()).datetime().replace(tzinfo=timezone('UTC')).astimezone(timezone(tzone))
            sunset = observer.next_setting(ephem.Sun()).datetime().replace(tzinfo=timezone('UTC')).astimezone(timezone(tzone))
            observer.horizon = '-6'
            civil_twilight_start = observer.next_rising(ephem.Sun(), use_center=True).datetime().replace(tzinfo=timezone('UTC')).astimezone(timezone(tzone))
            civil_twilight_end = observer.next_setting(ephem.Sun(), use_center=True).datetime().replace(tzinfo=timezone('UTC')).astimezone(timezone(tzone))
            observer.horizon = '-12'
            nautical_twilight_start = observer.next_rising(ephem.Sun(), use_center=True).datetime().replace(tzinfo=timezone('UTC')).astimezone(timezone(tzone))
            nautical_twilight_end = observer.next_setting(ephem.Sun(), use_center=True).datetime().replace(tzinfo=timezone('UTC')).astimezone(timezone(tzone))
            observer.horizon = '-18'
            astronomical_twilight_start = observer.next_rising(ephem.Sun(), use_center=True).datetime().replace(tzinfo=timezone('UTC')).astimezone(timezone(tzone))
            astronomical_twilight_end = observer.next_setting(ephem.Sun(), use_center=True).datetime().replace(tzinfo=timezone('UTC')).astimezone(timezone(tzone))

            print("astronomical_start", astronomical_twilight_start.strftime(tfmt), sep='\t', file=f)
            print("nautical_start", nautical_twilight_start.strftime(tfmt), sep='\t', file=f)
            print("civil_start", civil_twilight_start.strftime(tfmt), sep='\t', file=f)
            print("sunrise", sunrise.strftime(tfmt), sep='\t', file=f)
            print("sunset", sunset.strftime(tfmt), sep='\t', file=f)
            print("civil_end", civil_twilight_end.strftime(tfmt), sep='\t', file=f)
            print("nautical_end", nautical_twilight_end.strftime(tfmt), sep='\t', file=f)
            print("astronomical_end", astronomical_twilight_end.strftime(tfmt), sep='\t', file=f)
            observer.date = observer.date + 1

if __name__ == '__main__':
    calc_twilight_time()