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

    # Read the HTML as json and convert to dataframe
    try:
        df = pd.read_json(StringIO(html))
        # Convert the 1st column as header
        df.columns = df.iloc[0]
        df = df[1:]
    except:
        return rec

    # Read in the kp_cutoff from the line if provided
    bz_cutoff = 7
    if line:
        ele = line.strip().split('\t')
        if len(ele) >= 2:
            try:
                bz_cutoff = int(ele[1])
            except:
                pass

    # Find the minimal value in the column 'bz_gsm', and get the values in 'time_tag' and 'bz_gsm' columns
    df['bz_gsm'] = pd.to_numeric(df['bz_gsm'], errors='coerce')
    bz_min = df['bz_gsm'].min()
    time_tag_min = df.loc[df['bz_gsm'] == bz_min, 'time_tag'].values[0]

    # Get the time_tag in the last line
    time_tag_now = df.iloc[-1]['time_tag']

    # If bz_min is less than or equal to bz_cutoff, prepare the message
    if bz_min < bz_cutoff:
        # Set the value
        tid = time_tag_min
        # Only keep the date, hour and minute in msg time tags, the orignal format is like '2026-01-21 02:39:00.000'
        time_tag_min = re.sub(r':\d{2}\.\d{3}$', '', time_tag_min)
        time_tag_now = re.sub(r':\d{2}\.\d{3}$', '', time_tag_now)
        msg = f'Bz = {bz_min} nT  :  {time_tag_min} (UTC)  :  current time {time_tag_now} (UTC).'
        rec.append([surl, tid, msg, str(bz_min)])

    return rec

def get_email_title():
    return 'Bz Alert'

def compare_record(record, item, line = None):
    if not record or len(record) == 0:
        return True
    # Get the Bz cutoff from the line if provided
    bz_cutoff = -10
    time_diff_cutoff = 60  # in minutes
    if line:
        ele = line.strip().split('\t')
        if len(ele) >= 2:
            try:
                bz_cutoff = float(ele[1])
            except:
                pass

    print(f'Comparing record for item ID {item} with Bz cutoff {bz_cutoff} nT.')

    # Extract the Kp value from item[3]
    if len(item) >= 4:
        try:
            bz_min = bz_cutoff
            time_tag_min = item[1]
            time_tag = item[1]
            bz_value = float(item[3])
            for rec in record:
                if len(rec) >= 4:
                    try:
                        existing_bz = float(rec[3])
                        existing_time_tag = rec[1]
                        if existing_bz < bz_min:
                            bz_min = existing_bz
                            time_tag_min = existing_time_tag 
                    except:
                        pass
            
            # If the new bz_value is less than the minimal existing bz_min and the time_tag is different enough, return True
            time_diff = pd.to_datetime(time_tag) - pd.to_datetime(time_tag_min)
            time_diff_minutes = time_diff.total_seconds() / 60.0

            if bz_value < bz_min and time_diff_minutes >= time_diff_cutoff:
                return True

        except:
            pass

    return False
