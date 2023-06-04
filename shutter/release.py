# Usage: transmit the shutter release signal to shutter remote via HackRF

# Usage: python release.py -d <data> -f <frequency> -s <sample_rate> -a <amplifer> --lna <LNA gain> --vga <VGA gain> --tx <TXVGA gain> -r <repeat>

import argparse
import pylibhackrf, ctypes

# Parse arguments
parser = argparse.ArgumentParser(description='Transmit the shutter release signal to shutter remote via HackRF')
parser.add_argument('-d', '--data', type=str, help='data file to transmit', required=True)
parser.add_argument('-f', '--frequency', type=int, help='transmit frequency', default=2438000000)
parser.add_argument('-s', '--sample_rate', type=int, help='sample rate', default=5000000)
parser.add_argument('-a', '--amplifer', type=bool, help='amplifer', default=False)
parser.add_argument('-l', '--lna', type=int, help='LNA gain', default=16)
parser.add_argument('-v', '--vga', type=int, help='VGA gain', default=20)
parser.add_argument('-t', '--tx', type=int, help='TXVGA gain', default=30)
parser.add_argument('-r', '--repeat', type=int, help='repeat times', default=0)
args = parser.parse_args()

# Initialize HackRF
hackrf = pylibhackrf.HackRf()
if hackrf.is_open == False:
    hackrf.setup()
hackrf.set_freq(args.frequency)
hackrf.set_sample_rate(args.sample_rate)
hackrf.set_amp_enable(args.amplifer)
hackrf.set_lna_gain(args.lna)
hackrf.set_vga_gain(args.vga)
hackrf.set_txvga_gain(args.tx)

# Callback function
def callback_fun(hackrf_transfer):
    # Read data from file, each byte is a signed int8; loop through the data and convert to signed integer
    with open(args.data, 'rb') as f:
        data = f.read()
    data = [ctypes.c_int8(x).value for x in data]
    iq = hackrf.packed_bytes_to_iq(data)
    return 0
    

if __name__ == '__main__':
    # Transmit
    hackrf.start_tx_mode(callback_fun)
    #callback_fun(None)