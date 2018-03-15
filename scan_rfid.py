#!/usr/bin/env python3
from __future__ import print_function
import time
import sys
import mercury
import subprocess
reader = mercury.Reader("tmr:///dev/ttyUSB0", baudrate=115200)

runtime = 10
region = "NA2"
protocol = "GEN2"
power = 1900
credentials = "drone:36024pAbxHY"
post_url = "http://team21.cs.wright.edu:8000/rfid/api/v1/inventory/posttag"
antenna = 1
#tag = "3"

print("Model:", reader.get_model())
print("Supported Regions:", reader.get_supported_regions())

reader.set_region(region)
reader.set_read_plan([antenna], protocol, read_power=power)
#print(reader.read())

#tag = "tag="+tag
#print(tag)
#subprocess.call(['curl', '-u', credentials,'-d', tag, '-X', 'POST', post_url])

#reader.start_reading(lambda tag: print(tag.epc, tag.antenna, tag.read_count, tag.rssi))
try:
    reader.start_reading(lambda tag: subprocess.call(['curl','-u',credentials,'-d',"tag="+tag.epc.decode("utf-8"),'-X','POST',post_url]))
    time.sleep(runtime)
    reader.stop_reading()
    sys.exit()
except KeyboardInterrupt:
    print("KB interrupt detected: exiting")
    sys.exit()
sys.exit()
