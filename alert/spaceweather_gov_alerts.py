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
    # For each item in the '{...}' blocks
    items = re.findall(r'\{(.+?)\}', html, re.MULTILINE|re.DOTALL)
    tid, ttime, tmsg = None, None, None
    for item in items:
        # Find "product_id":"..."
        m = re.search(r'"product_id"\s*:\s*"([^"]+)"', item)
        if m:
            tid = m.group(1) 
        # Find "issue_datetime":"..."
        m = re.search(r'"issue_datetime"\s*:\s*"([^"]+)"', item)
        if m:
            ttime = m.group(1)
        # Find "message":"..."
        m = re.search(r'"message"\s*:\s*"([^"]+)"', item)
        if m:
            tmsg = m.group(1)

        if tid and ttime and tmsg:
            tid = tid + '_' + ttime
            msg = tmsg
            # Replace '\r\n' with space
            msg = re.sub(r'\\r\\n', ' | ', msg)
            rec.append([surl, tid, msg])
    return rec

def get_email_title():
    return 'spaceweather.gov Alerts'
