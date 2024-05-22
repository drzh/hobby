'''
Convert the RSS XML file from 'in-the-sky.org' to a table.

Usage:

python3 convert_occultation_xml_to_table.py -i <input.url> -o <output.tsv>
    Input file: URLs of the RSS feed. It can have comments and empty lines.
'''

import click
import feedparser
import pandas as pd

@click.command()
@click.option('-i', '--input_file', required=True, type=click.File(), help='Input file')
@click.option('-o', '--output_file', required=True, type=click.Path(), help='Output file')

def main(input_file, output_file):
    urls = [line.strip() for line in input_file if line.strip() and not line.startswith('#')]
    data = []
    for url in urls:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            data.append(extract_data(entry))
    df = pd.DataFrame(data)
    # Sort by date
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by='date', ascending=True)
    df.to_csv(output_file, sep='\t', index=False)

def extract_data(entry):
    data = {}
    data['title'] = entry['title']
    data['description'] = entry['summary']
    data['link'] = entry['link']
    data['date'] = entry['published']
    return data

if __name__ == '__main__':
    main()
