'''
Calculate the RA/DEC of a celestial object from its elements

Usage: calc_RA_DEC_from_elements.py -i <input_file> -o <output_file>

Options:
    -i, --input_file    Input tsv file (with head, default is stdin):
                            Column 1: Comet name
                            Column 2: yyyy-m-d.d
    -o, --output_file   Output tsv file (default is stdout) containing the RA/DEC of the celestial objects
'''

import sys
import click
import numpy as np
import skyfield.api as sf
from skyfield.api import load
from skyfield.data import mpc

def calc_RA_DEC_from_elements(input_file, output_file):
    # Load the orbital elements\
    with load.open(mpc.COMET_URL, reload=True) as f:
        print('Loading the orbital elements from:', mpc.COMET_URL, file=sys.stderr)
        comets = mpc.load_comets_dataframe(f)

    print(len(comets), 'comets loaded', file=sys.stderr)

    # Keep only the most recent orbit for each comet,
    # and index by designation for fast lookup.
    comets = (comets.sort_values('reference')
              .groupby('designation', as_index=False).last()
              .set_index('designation', drop=False))

    eph = load('de421.bsp')
    sun, earth = eph['sun'], eph['earth']

    with open(output_file, 'w') as of:
        with open(input_file, 'r') as f:
            for line in f:
                comet_name, dt = line.rstrip().split('\t')
                yy, mm, dd = dt.split('-')
                yy, mm, dd = int(yy), int(mm), float(dd)

                row = comets.loc[comet_name]

                ts = load.timescale()

                from skyfield.constants import GM_SUN_Pitjeva_2005_km3_s2 as GM_SUN
                comet = sun + mpc.comet_orbit(row, ts, GM_SUN)

                t = ts.utc(yy, mm, dd)
                ra, dec, distance = earth.at(t).observe(comet).radec()
                ra = str(ra.to(unit='degree'))[:-4]
                dec = str(dec.to(unit='degree'))[:-4]
                print(comet_name, str(yy) + '-' + str(mm) + '-' + str(dd), ra, dec, sep='\t', file=of)


@click.command()
@click.option('-i', '--input_file', type=click.Path(exists=True), help='Input tsv file containing the orbital elements', default='/dev/stdin')
@click.option('-o', '--output_file', type=click.Path(), help='Output tsv file containing the RA/DEC of the celestial objects', default='/dev/stdout')

def main(input_file, output_file):
    calc_RA_DEC_from_elements(input_file, output_file)

if __name__ == '__main__':
    main()
