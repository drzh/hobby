"""
1. Grab a webpage from dallas.cragslist.org based on the URLs in the file
2. Extract the item name, price, and URL for each item
3. Check whether the item is in the SQLite3 database
4. If the item is not in the database, send an email via gmail to the user and add the item to the database

Usage: python report.py -w <website_module> -u <URLs file> -d <database file>

URLs file: A file containing the URLs to check, one per line
Database file: A SQLite3 database file containing the items URLs that have already been checked
"""

import sys
import urllib3
import re
import smtplib
import os.path
import argparse
import importlib
import datetime
from db import DB
from sendemail import sendemail

def parse_args():
    parser = argparse.ArgumentParser(description="Check webpages for new items and send email alerts.")
    parser.add_argument("-w", "--website_module", required=True, help="Website module to use (e.g., spaceweather_gov)")
    parser.add_argument("-u", "--urls_file", required=True, help="File containing the list of URLs to check")
    parser.add_argument("-d", "--db_file", required=True, help="SQLite3 database file")
    return parser.parse_args()

# Fucntion to check whether the file exists
def check_file(file):
    if not os.path.isfile(file):
        print("The file %s does not exist" % file)
        sys.exit(1)

# Fuction to get html content from a URL
def get_html(url):
    try:
        http = urllib3.PoolManager()
        response=http.request('GET', url)
        return response.data.decode('utf-8')
    except urllib3.exceptions.HTTPError as e:
        print('Request failed:', e.reason)
        sys.exit(1)

# Main function
def main():
    # Parse the command line arguments
    args = parse_args()

    # Import the website module
    ws = importlib.import_module(f'{args.website_module}')
    
    # Check whether the files exist
    if args.urls_file:
        check_file(args.urls_file)
    if args.db_file:
        check_file(args.db_file)

    # Connect to the SQLite3 database
    db = DB(args.db_file)

    # Create a table ITEMS if it does not exist, with columns SURL, TURL, NAME, PRICE, and TIME
    db.create_table('ITEMS', ws.get_db_columns())

    # Read the URLs file, and skip the lines starting with # and empty lines
    rec = []
    surls = []
    with open(args.urls_file, 'r') as urls_file:
        for line in urls_file:
            line = line.strip()
            if line.startswith('#') or line == '':
                continue
            surls.append(line)

    # Loop through the URLs
    for line in surls:
        surl = line.split('\t')[0]
        # Grab the webpage
        html = get_html(surl)

        # Extract the items from the HTML
        items = ws.get_items_from_html(surl, html, line)

        # Loop through the items
        for item in items:
            # Check whether the item is in the database
            result = db.select('ITEMS', where=f'ID="{item[0]}"')

            # If the item is not in the database, add it to the record
            if result == []:
                rec.append([surl] + item)
            
    # If there are new items, send an email to the user
    if len(rec) == 0:
        sys.exit(0)
        
    # The subject of the email is 'CL Alert' and the body of the email is the list of new items
    msg = '\n'
    for item in rec:
        # Format item[0] to HTML
        msg += f"{item[2]}\n\n"

    # send the email
    if sendemail(ws.get_email_title(), msg):
        # Add the new items to the database
        for item in rec:
            db.insert('ITEMS', ws.get_db_columns().keys(), item + [str(datetime.datetime.now())])

        # For each surl, only keep the latest 1000 records
        db.keep_records('ITEMS', column_group='URL', column_order='TIME', number=1000)

    # Close the database connection
    db.close()

if __name__ == "__main__":
    main()
