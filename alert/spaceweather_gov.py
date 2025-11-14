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
    # Extract all '<div class="views-content-title">...<div class="views-content-changed">...</div>' items
    items = re.findall(r'(<div class="views-content-title">.*?<div class="views-content-changed">.*?</div>)', html, re.DOTALL)
    for item in items:
        date_match = re.search(r'<div class="views-content-changed">(.+?)</div>', item, re.DOTALL)
        date_str = ''
        # Remove HTML tags from date_match
        if date_match:
            date_str = re.sub(r'<[^>]+>', '', date_match.group(1)).strip()
        title_match = re.search(r'<div class="views-content-title">.*?<a href="([^"]+)">(.+?)</a>', item, re.DOTALL)
        name = ''
        turl = ''
        if title_match:
            title = title_match.group(2).strip()
            turl = surl + title_match.group(1).strip()
            tid = f"{title} - {date_str}"
            msg = f"{title} : {turl} : {date_str}"
            rec.append([surl, tid, msg])
    return rec

def get_email_title():
    return 'spaceweather.gov Alert '
