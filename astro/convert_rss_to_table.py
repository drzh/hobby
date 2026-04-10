'''
Convert the RSS XML file from 'in-the-sky.org' to a table.

Usage:

python3 convert_occultation_xml_to_table.py -i <input.url> -o <output.tsv>
    Input file: URLs of the RSS feed. It can have comments and empty lines.
'''

import click
import feedparser
import pandas as pd
from email.utils import parsedate_to_datetime

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
    # Sort by date: ensure datetimes are parsed (coerce invalid values) and normalized to UTC
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'], utc=True, errors='coerce')
    df = df.sort_values(by='date', ascending=True)
    df.to_csv(output_file, sep='\t', index=False)

def extract_data(entry):
    data = {}
    data['title'] = entry.get('title', '')
    data['description'] = entry.get('summary', '')
    data['link'] = entry.get('link', '')
    # prefer published, fall back to updated; parse RFC-2822 style dates into datetimes
    pub = entry.get('published') or entry.get('updated') or ''
    if pub:
        try:
            data['date'] = parsedate_to_datetime(pub)
        except Exception:
            # keep original string if parsing fails; pandas.to_datetime with errors='coerce' will handle it later
            data['date'] = pub
    else:
        data['date'] = pd.NaT
    return data
    return data

if __name__ == '__main__':
    main()
