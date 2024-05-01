'''
Calculate the rise and set time of a celestial object from its RA/DEC

Usage: calc_rise_set_from_RA_DEC.py -i <input_RA_DEC_file> -l <input_lon_lat> -o <output_file>

Options:
    -i, --input_file    Input tsv file (no head, default is stdin):
                            Column 1: Comet name
                            Column 2: yyyy-m-d
                            Column 3: RA
                            Column 4: DEC
    -l, --input_lon_lat Input tsv file
                            Column 1: Position name
                            Column 2: Longitude
                            Column 3: Latitude
    -o, --output_file   Output tsv file (default is stdout) containing the rise and set time of the celestial objects
'''

import sys
import click
import numpy as np
#import skyfield.api as sf
from skyfield.api import load
from astropy.coordinates import SkyCoord
from astropy.coordinates import EarthLocation
from astropy.time import Time
from astroplan import Observer
import astropy.units as u
from datetime import datetime, timedelta

def calc_rise_set_from_RA_DEC(input_file, input_lon_lat, output_file):
    lon_lat = []

    with open(input_lon_lat, 'r') as llf:
        for line in llf:
            position_name, lon, lat = line.rstrip().split('\t')
            lon_lat.append([position_name, float(lon), float(lat)])

    with open(input_file, 'r') as rdf:
        for line in rdf:
            comet_name, dt, ra, dec = line.rstrip().split('\t')
            date_fraction, time_fraction = dt.split('.')
            date_fmt = datetime.strptime(date_fraction, '%Y-%m-%d')
            hour_fmt = timedelta(hours=int(time_fraction) * 60 / 100)
            dt_fmt = date_fmt + hour_fmt
            ra, dec = float(ra), float(dec)
            t = Time(dt_fmt)
            c = SkyCoord(ra=ra, dec=dec, unit='deg')

            for j in range(len(lon_lat)):
                observer = Observer(longitude=lon_lat[j][1]*u.deg, latitude=lon_lat[j][2]*u.deg)
                rise_time = observer.target_rise_time(t, c, which='nearest')
                print(comet_name, dt, ra, dec, position_name, lon_lat[j][1], lon_lat[j][2], 'rise', rise_time.iso, sep='\t')
                set_time = observer.target_set_time(t, c, which='nearest')
                print(comet_name, dt, ra, dec, position_name, lon_lat[j][1], lon_lat[j][2], 'set', set_time.iso, sep='\t')

@click.command()
@click.option('-i', '--input_file', type=click.Path(exists=True), help='Input tsv file containing the RA/DEC of the celestial objects', default='/dev/stdin')
@click.option('-l', '--input_lon_lat', type=click.Path(exists=True), help='Input tsv file containing the longitude and latitude of the observer', default='/dev/stdin')
@click.option('-o', '--output_file', type=click.Path(), help='Output tsv file containing the rise and set time of the celestial objects', default='/dev/stdout')

def main(input_file, input_lon_lat, output_file):
    calc_rise_set_from_RA_DEC(input_file, input_lon_lat, output_file)

if __name__ == '__main__':
    main()
