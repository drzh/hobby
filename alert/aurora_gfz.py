# Define the database columns for the ITEMS table
import re
import pandas as pd
from io import StringIO

def get_db_columns():
    return {
        'URL': 'TEXT',
        'ID': 'TEXT',
        'MSG': 'TEXT',
        'VALUE': 'TEXT'
    }

def get_items_from_html(surl, html, line = None):
    rec = []

    # Read in the HTML content as CSV using pandas
    df = pd.read_csv(StringIO(html))

    # Read in the kp_cutoff from the line if provided
    kp_cutoff = 7
    if line:
        ele = line.strip().split('\t')
        if len(ele) >= 2:
            try:
                kp_cutoff = int(ele[1])
            except:
                pass

    # Keep only the rows where 'maximum' column is greater than or equal to kp_cutoff
    df = df[pd.to_numeric(df['maximum'], errors='coerce') >= kp_cutoff]

    # For each row in the filtered dataframe, create a record with 'Time (UTC)' and 'maximum' as a list
    rec = []
    for index, row in df.iterrows():
        tid = row['Time (UTC)']
        # Reformat tid from 'DD-MM-YYYY HH:MM' to 'YYYY-MM-DD HH:MM'
        tid_m = re.match(r'(\d{2})-(\d{2})-(\d{4}) (\d{2}:\d{2})', tid)
        if tid_m:
            tid = f"{tid_m.group(3)}-{tid_m.group(2)}-{tid_m.group(1)} {tid_m.group(4)}"
        kp_value = row['maximum']
        msg = f"Maximum Kp = {kp_value} at {tid} <br/><br/>"
        rec.append([surl, tid, msg, str(kp_value)])
    
    return rec

def get_email_title():
    return 'GFZ Aurora Alert'

def compare_record(record, item, line = None):
    # Extract the Kp value from item[3]
    if len(item) >= 4:
        try:
            kp_value = float(item[3])
            
            # Find the max Kp value in the existing record
            max_kp = -1
            for rec in record:
                if len(rec) >= 4:
                    try:
                        existing_kp = float(rec[3])
                        if existing_kp > max_kp:
                            max_kp = existing_kp
                    except:
                        pass
            
            # If the new kp_value is greater than max_kp, return True
            if kp_value > max_kp:
                    return True
        except:
            pass

    return False
