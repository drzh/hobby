'''
Usage: Calculate the geomagnetic latitude, longitude for a given geographic location and date using the World Magnetic Model (WMM).

Usage: python3 calc_geomag_lat_long_decl_incl.py -i <file_with_lat_long> --latcol <lat_column_> --loncol <lon_column> -y <year_epoch> -o <output_file>

'''

import click
import pandas as pd
from geomaglib import sh_loader, magmath, dipole
from pygeomag import GeoMag

@click.command()
@click.option('-i', '--inputfile', default='/dev/stdin', type=click.Path(exists=True), help='Input file containing latitude and longitude data.')
@click.option('-o', '--outputfile', default='/dev/stdout', type=click.Path(), help='Output file to save the results.')
#@click.option('-m', '--wmm', default='WMM2025.COF', type=str, help='WMM coefficient file')
@click.option('--latcol', default=3, help='Column number for latitude in the input file.')
@click.option('--loncol', default=2, help='Column number for longitude in the input file.')
#@click.option('--altcol', default=None, help='Column number for altitude in kilometers in the input file. If not provided, altitude is assumed to be 0 km.')
@click.option('-y', '--year', default=2025.0, type=float, help='Year epoch for the geomagnetic model.')

def calc_geomag(inputfile, outputfile, latcol, loncol, year):
    # Dipole model for geomagnetic lat/lon
    dp = dipole.Dipole(year)

    with open(inputfile, 'r') as infile, open(outputfile, 'w') as outfile:
        for line in infile:
            ele = line.strip().split('\t')
            try:
                lat = float(ele[int(latcol) - 1])
                lon = float(ele[int(loncol) - 1])

                # Geomagnetic latitude and longitude
                mlat, mlon = dp.coords(lat, lon)

                # Write results to output file
                outfile.write("\t".join(ele) + f"\t{mlon:.3f}\t{mlat:.3f}\n")
            except Exception as e:
                print(f"Error processing line: {line.strip()} - {e}")
                return False

    return True


if __name__ == '__main__':
    calc_geomag()
                