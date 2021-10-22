"""
This example sets an upper and lower temperature limit and checks if the
temperature is outside the limits.

* Author: Trevor Sprague
"""

import tmp117_ftdi as tmp
from time import sleep

t = tmp.TMP117()
t.soft_reset()  # software reset high/low temp limit = 192*C/-256*C


# read the alert flag BEFORE it's cleared by other commands:
# when in alert mode (therm mode off)
# if the high/low limit is crossed (alert = 1), but the config reg
# is read in a different command prior to isHighAlert()/isLowAlert(),
# then the alert will be read as 0

# get conversion time
conv_time = t.get_conversion_time()
print("Conversion time: {} sec".format(conv_time))

# set high/low limits to +/-10C from current temperature
t.set_temp_offset(0)
sleep(conv_time)
init_temp = t.read_tempC()
t.set_temp_high_limit(init_temp + 10)
t.set_temp_low_limit(init_temp - 10)

# display temperature limits
print("\nHigh temp limit: {h:.2f}C\nLow temp limit: {l:.2f}C\n"
    .format(h=t.get_temp_high_limit(), l=t.get_temp_low_limit()))
sleep(2)


# Both high and low alerts can be checked simultaneously with:
# ts.getHighLowAlert()
# Running any of isLowAlert(), isHighAlert(), getHighLowAlert()
# clears the config register, so only one can be used per reading

# increment offset past the upper limit to force the high alert
# (this allows limits to be tested without physically changing the temp)
for i in range(0, 21, 2):
    t.set_temp_offset(i)
    sleep(conv_time)    # wait until the reading is complete
    
    print("{offset}C offset, temp: {temp:.2f}"
        .format(offset=t.get_temp_offset(), temp=t.read_tempC()))
    print("High alert: {}".format(t.is_high_alert()))

# decrement offset past the lower limit to force the low alert
# (this allows limits to be tested without physically changing the temp)
for i in range(0, -21, -2):
    t.set_temp_offset(i)
    sleep(conv_time)    # wait until the reading is complete
    
    print("{offset}C offset, temp: {temp:.2f}"
        .format(offset=t.get_temp_offset(), temp=t.read_tempC()))
    print("Low alert: {}".format(t.is_low_alert()))

t.close()