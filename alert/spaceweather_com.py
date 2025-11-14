# Define the database columns for the ITEMS table
import re

def get_db_columns():
    return {
        'URL': 'TEXT',
        'ID': 'TEXT',
        'MSG': 'TEXT',
        'TIME': 'TEXT'
    }

def get_items_from_html(surl, html, line = None):
    rec = []
    
    # Extract all '<p ...><strong>...</p>'
    items = re.findall(r'<p [^>]+>(<strong>.+?)</p>', html, re.MULTILINE|re.DOTALL)
    for item in items:
        # Remove html tags from item
        item = re.sub(r'<[^>]+>', '', item).strip()
        tid = item
        msg = item
        rec.append([surl, tid, msg])
    return rec

def get_email_title():
    return 'spaceweather.com Alert'
