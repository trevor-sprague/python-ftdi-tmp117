"""
This example sets a variety of conversion times and averaging samples.

* Author: Trevor Sprague
"""

import tmp117_ftdi as tmp
from time import sleep

# This returns the number of samples averaged
# rather than the bits in the config register
num_samples = {
    0: 1,
    1: 8,
    2: 32,
    3: 64,
}

t = tmp.TMP117()
t.soft_reset()  # software reset high/low temp limit = 192*C/-256*C


# Iterate through all conversion time and sample averaging combinations.
# The conversion cycle time is how long between readings.
# Averaging is how many readings average together.
# See end of example for list of cc times and averaging samples.

for i in range(0, 4):
    t.set_averaging(i)
    print("{} samples will be averaged."
        .format(num_samples[t.get_averaging()]))

    for j in range(0, 8):
        t.set_conversion_cycle_time(j)
        conv_time = t.get_conversion_time()

        sleep(conv_time)
        print("{time} sec convertion time, temp: {temp:.2f}C"
            .format(time=conv_time, temp=t.read_tempC()))

t.close()

# Accepted args for setting number of samples to average (default 1)
#   avgNone = 0 === take a single reading
#   avg8 = 1 === average 8 readings
#   avg32 = 2 === average 32 readings
#   avg64 = 3 === average 64 readings

# Accepted args for setting conversion cycle time (default 1s)
#   conv15p5ms = 0b000 === conversion cycle takes 15.5ms
#   conv125ms = 0b001 === ...takes 125ms
#   conv250ms = 0b010 === ...takes 250ms
#   conv500ms = 0b011 === ...takes 500ms
#   conv1s = 0b100 === ...takes 1000ms
#   conv4s = 0b101 === ...takes 4000ms
#   conv8s = 0b110 === ...takes 8000ms
#   conv16s = 0b111 === ...takes 16000ms