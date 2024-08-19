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

def calc_moon_time(lat, lon, dstart, dend, tz, output):
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
            observer.date = observer.next_rising(ephem.Moon())
            moonrise = observer.date.datetime().replace(tzinfo=timezone('UTC')).astimezone(timezone(tzone))
            observer.date = observer.next_transit(ephem.Moon())
            moontransit = observer.date.datetime().replace(tzinfo=timezone('UTC')).astimezone(timezone(tzone))
            # Moon phase at transit
            moon = ephem.Moon()
            moon.compute(observer)
            phase = moon.phase
            observer.date = observer.next_setting(ephem.Moon())
            moonset = observer.date.datetime().replace(tzinfo=timezone('UTC')).astimezone(timezone(tzone))
            print("moon_rise", moonrise.strftime(tfmt), sep='\t', file=f)
            print("moon_transit", moontransit.strftime(tfmt) + ' (phase=' + "%.1f" % phase + ')', sep='\t', file=f)
            print("moon_set", moonset.strftime(tfmt), sep='\t', file=f)

if __name__ == '__main__':
    calc_moon_time()