'''
Usage: Query the geomagnetic latitude, longitude for a given geographic location using HTTP GET request:
       https://gifs-api.bgs.ac.uk/geomagnetic-coordinates/point?latitude=0&longitude=0&altitude=0&decimal_year=2025

HTTP Json output example:
{"metadata":{"geographic-latitude":0.0,"geographic-longitude":0.0,"altitude":"0.0 km","epoch":2025.0,"datum":"WGS84 ellipsoid","IGRF-version":14},"data":{"dipole":{"latitude":2.737,"longitude":72.972},"quasi-dipole":{"latitude":-13.301,"longitude":74.205}}}

Usage: python3 query_geomag_lat_long.py -i input.txt -o output.txt --latcol 3 --loncol 2 -y 2025.0

'''

import sys
import click
import requests

@click.command()
@click.option('-i', '--inputfile', default='/dev/stdin', type=click.Path(exists=True), help='Input file containing latitude and longitude data.')
@click.option('-o', '--outputfile', default='/dev/stdout', type=click.Path(), help='Output file to save the results.')
@click.option('--latcol', default=3, help='Column number for latitude in the input file.')
@click.option('--loncol', default=2, help='Column number for longitude in the input file.')
@click.option('--altcol', default=None, help='Column number for altitude in the input file. If not provided, altitude is assumed to be 0.')
@click.option('-y', '--year', default=2025.0, type=float, help='Year epoch for the geomagnetic model.')

def query_geomag(inputfile, outputfile, latcol, loncol, altcol, year):
    with open(inputfile, 'r') as infile, open(outputfile, 'w') as outfile:
        for line in infile:
            ele = line.strip().split('\t')
            try:
                lat = float(ele[latcol - 1])
                lon = float(ele[loncol - 1])
                altitude = 0.0  # Default altitude
                if altcol is not None:
                    alt = float(ele[altcol - 1])
                else:
                    alt = 0.0
                
                # Construct the request URL
                url = f"https://gifs-api.bgs.ac.uk/geomagnetic-coordinates/point?latitude={lat}&longitude={lon}&altitude={alt}&decimal_year={year}"
                
                # Make the GET request
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    geomag_lat = data['data']['dipole']['latitude']
                    geomag_lon = data['data']['dipole']['longitude']
                    
                    # Write the results to the output file
                    outfile.write("\t".join(ele) + f"\t{geomag_lon}\t{geomag_lat}\n")
                else:
                    # Handle HTTP errors to stderr
                    print(f"Error fetching data for lat: {lat}, lon: {lon}. HTTP Status Code: {response.status_code}", file=sys.stderr)
            except Exception as e:
                print(f"Error processing line: {line.strip()}. Error: {e}", file=sys.stderr)


if __name__ == '__main__':
    query_geomag()
