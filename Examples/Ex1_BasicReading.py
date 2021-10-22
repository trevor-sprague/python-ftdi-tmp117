"""
Simple example for capturing and printing temperature in C and F

* Author: Trevor Sprague
"""

import tmp117_ftdi as tmp
import time
from string import Template

t = tmp.TMP117()
p = Template("Temp = $temp$temp_str")

# 5min (300sec) timeout
timeout = time.monotonic() + 300

while(time.monotonic() < timeout):
    while(not t.is_data_ready()): continue  # wait for reading
    print(p.substitute(temp=round(t.read_tempC(),2), temp_str="C"))
    print(p.substitute(temp=round(t.read_tempF(),2), temp_str="F"))
    print("")

t.close()   # terminate connection to tmp117