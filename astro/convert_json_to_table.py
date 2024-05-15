'''
Convert JSON to table

Usage: python convert_json_to_table.py -i <input_file> -o <output_file> -k <key>

Input file: json
Output file: tsv
Key: key to extract from json. Multiple levels of keys can be separated by comma.
'''

import json
import pandas as pd
import click

def extract_key(data, key):
    for k in key.split(','):
        data = data[k]
    return data

@click.command()
@click.option('-i', '--input_file', required=True, type=click.Path(exists=True), help='Input file')
@click.option('-o', '--output_file', required=True, type=click.Path(), help='Output file')
@click.option('-k', '--key', required=True, help='Key to extract from json')

def main(input_file, output_file, key):
    with open(input_file, 'r') as f:
        data = json.load(f)
        data = extract_key(data, key)
        df = pd.DataFrame(data)
        df.to_csv(output_file, sep='\t', index=False)

if __name__ == '__main__':
    main()
