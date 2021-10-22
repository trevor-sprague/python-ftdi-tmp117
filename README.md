# python-ftdi-tmp117
TMP117 python library, interfacing via FTDI

## Dependencies
This driver requires:
- [pyftdi](https://github.com/eblot/pyftdi)

Setup FTDI interface typically requires:
- [pyusb](https://github.com/pyusb/pyusb)
- [libusb](https://github.com/libusb/libusb)

[This is a useful setup guide](https://learn.adafruit.com/circuitpython-on-any-computer-with-ft232h/setup)
for FT232H devices (Blinka is not required for this driver to function)

## Example Usage

```python
import tmp117_ftdi as tmp

t = tmp.TMP117()
t.soft_reset()  # reset settings

while(True):
    while(not t.is_data_ready()): continue
    print("Temp = {:.2f}C".format(t.read_tempC()))
```