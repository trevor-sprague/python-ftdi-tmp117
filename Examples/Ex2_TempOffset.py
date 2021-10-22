"""
This example sets a variety of temperature offsets and captures the
temperature at each offset (in degrees celcius).

* Author: Trevor Sprague
"""

import tmp117_ftdi as tmp

t = tmp.TMP117()
t.soft_reset()  # software reset high/low temp limit = 192*C/-256*C

t.set_temp_offset(0)    # set 0C offset
t.read_tempC()  # clear data registers
while(not t.is_data_ready()): continue  # wait until data ready
print("Initial temp: {:.2f}C\n".format(t.read_tempC()))

# increase temperature offset from -10C to 10C in 1C increments
# and take measurements at each offset
for i in range(-10, 11):
    t.set_temp_offset(i)

    while(not t.is_data_ready()): continue
    print("{offset}C offset, temp: {temp:.2f}"
        .format(offset=t.get_temp_offset(), temp=t.read_tempC()))

t.close()