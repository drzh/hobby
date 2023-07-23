#!/usr/bin/env python

import datetime
import asyncio
import subprocess
from canoremote import CanoRemote, Button, Mode

MODE=Mode.Immediate
#MODE=Mode.Delay
#MODE=Mode.Movie

# 6D2
addr = "D4:53:83:13:CE:66"

# 90D
#addr = "74:7A:90:AD:59:1A"

# SL2
#addr = "00:9D:6B:78:C5:64"

# RP
#addr = "70:74:14:08:37:12"

# R
#addr = "10:98:C3:32:B6:09"

async def run():
    async with CanoRemote(addr, timeout=5) as cr:

        print("Initialize ...")
        await cr.initialize()
        print('Connected:', cr.is_connected)
        print("Initialized")

        # Wait for 0.05 seconds
        await asyncio.sleep(2)

        ## Press the "focus" button for 600ms
        #print("Press focus")
        #await cr.state(MODE, Button.Focus)
        #await asyncio.sleep(0.6)
        #print("Release focus")
        #await cr.state(MODE)

        ## wait for 4 seconds
        #await asyncio.sleep(4)

        # Press the "shutter" button for 500ms
        # Repeat n times
        n = 10
        i = 0
        while i < n:
            # print current time in YYYY-MM-DD HH:MM:SSssssss format
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"), end=' ')
            
            print("Press shutter:", i)        
            await cr.state(MODE, Button.Release)
            await cr.state(MODE)
            await asyncio.sleep(0.55)
            i += 1

if __name__ == "__main__":
    #if 1: subprocess.call(['bluetoothctl','disconnect',addr])
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
    
