'''
Only keep the element overlapped with the given longitude and latitude range.

Usage:
    python3 trim_kml.py -i <input.kml> -o <output.kml> --minlon <min_lon> --maxlon <max_lon> --minlat <min_lat> --maxlat <max_lat>

'''

import click
import xml.etree.ElementTree as ET

@click.command()
@click.option('-i', '--input_file', required=True, help='Input KML file.')
@click.option('-o', '--output_file', required=True, help='Output KML file.')
@click.option('--minlon', 'min_lon', required=True, type=float, default=-128, help='Minimum longitude.')
@click.option('--maxlon', 'max_lon', required=True, type=float, default=-64, help='Maximum longitude.')
@click.option('--minlat', 'min_lat', required=True, type=float, default=23, help='Minimum latitude.')
@click.option('--maxlat', 'max_lat', required=True, type=float, default=49, help='Maximum latitude.')

def trim_kml(input_file, output_file, min_lon, max_lon, min_lat, max_lat):
    ns = 'http://www.opengis.net/kml/2.2'

    ET.register_namespace('', ns)

    tree = ET.parse(input_file)
    root = tree.getroot()
    for element in root[:]:
        for subelement in element[:]:
            for subsubelement in subelement[:]:
                if subsubelement.tag == '{' + ns + '}' + 'LatLonBox':
                    north = float(subsubelement.find('{' + ns + '}north').text)
                    south = float(subsubelement.find('{' + ns + '}south').text)
                    east = float(subsubelement.find('{' + ns + '}east').text)
                    west = float(subsubelement.find('{' + ns + '}west').text)
                    #print(north, south, east, west)
                    if north < min_lat or south > max_lat or east < min_lon or west > max_lon:
                        element.remove(subelement)
                #if subsubelement.tag == '{' + ns + '}' + 'color':
                    #subelement.remove(subsubelement)
    tree.write(output_file, encoding='utf-8')

if __name__ == '__main__':
    trim_kml()