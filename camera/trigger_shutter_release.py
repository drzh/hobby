# Usage: Trigger  accroding to the time schedule given by the input file
# Usage: python3 trigger_capture.py -i <input file> -l <sleep time interval between each run> -t <Binary_test> -p <harckrf_file_prefix> -s <HackRF sample rate> -f <HackRF frequency> -x <HackRF gain>
#       The input file should be a TSV file with the following columns (Time is in UTC):
#       1. The start date in the format of YYYYMMDD
#       2. The start time in the format of HHMMSS
#       3. The end date in the format of YYYYMMDD
#       4. The end time in the format of HHMMSS
#       5. The interval between two captures in seconds (can be a float)

import argparse
import subprocess
import datetime
import time
from lib.cameraremote import read_plan

# Parse the arguments
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', dest = 'input', help = 'Input file')
parser.add_argument('-l', '--sleep', dest = 'sleep', help = 'Sleep time interval between each run', type=float, default=0.01)
parser.add_argument('-p', '--prefix', dest = 'prefix', help = 'HarckRF file prefix')
parser.add_argument('-t', '--test', dest = 'test', help = 'Binary test', type=bool, default=False, action=argparse.BooleanOptionalAction)
parser.add_argument('-s', '--samplerate', dest = 'sleep', help = 'HackRF sample rate', type=float, default=5000000)
parser.add_argument('-f', '--frequency', dest = 'sleep', help = 'HackRF frequency', type=float, default=2438000000)
parser.add_argument('-x', '--gain', dest = 'sleep', help = 'HackRF gain', type=float, default=30)
args = parser.parse_args()

# Function to trigger the shutter release
def trigger_shutter_release(harckrf_file, test):
    if test:
        # If it is a test, do nothing
        print('Triggering - Test')
    else:
        # Otherwise, trigger the shutter release
        print('Triggering - ', harckrf_file, sep = '')
        # Call the trigger_capture.sh script
        subprocess.call(['hackrf_transfer', '-t', hackrf_file, '-s', args.samplerate, '-f', args.frequency, '-x', args.gain, '-R'])


# Main function
def main():
    # Read the time plan
    plan = read_plan(args.input)

    # Iterate through the time plan
    for item in plan:
        #print(item)
        # Sleep until the starting time
        proc = None
        now = datetime.datetime.utcnow()
        if item[0] > now:
            print('Sleeping until {}...'.format(item[0]))
            time.sleep((item[0] - now).total_seconds())
        elif now <= item[1]:
            hackrf_file = args.prefix + "{:.2f}".format(item[2]) + 's.harckrf'
            if test:
                # If it is a test, do nothing
                print('Test - ', end='')
            print(item[0].strftime('%Y-%m-%d %H:%M:%S.%f'), end=' ')
            print(item[1].strftime('%Y-%m-%d %H:%M:%S.%f'), end=' ')
            print(item[2])
            print('Triggering - ', hackrf_file, sep = '')
            if test:
                proc = subprocess.Popen('sleep 1000', shell=True)
            else:
                proc = subprocess.run(['hackrf_transfer', '-t', hackrf_file, '-s', args.samplerate, '-f', args.frequency, '-x', args.gain, '-R'])

            while now <= item[1]:
                time.sleep(args.sleep)
                now = datetime.datetime.utcnow()
                print(now.strftime('%Y-%m-%d %H:%M:%S.%f'), end='\r')
            
            # Stop the process
            if proc != None:
                proc.kill()
                proc.wait()

if __name__ == '__main__':
    main()
