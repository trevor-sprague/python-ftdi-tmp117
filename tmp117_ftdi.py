"""
`tmp117_ftdi`
========================================================================
Library for TMP117 temperature sensor
* Author: Trevor Sprague

Test Implementation Notes
--------------------
**Hardware:**
* `SparkFun High Precision Temperature Sensor - TMP117 (Qwiic)
    <https://www.sparkfun.com/products/15805>`
* `Adafruit FT232H Breakout - General Purpose USB to GPIO, SPI, I2C - 
    USB C & Stemma QT <https://www.adafruit.com/product/2264>`

**Software and Dependencies:**
* pyftdi

"""

import pyftdi.i2c
import enum
import struct
import time

_TEMP_CONVERSION_FACTOR = 0.0078125
_C_TO_F_CONVERSION_FACTOR = 1.8
_DEVICE_ID = 0X0117

class Reg(enum.IntEnum):
    TEMP =          0x00
    CFG =           0x01
    T_HIGH_LIMIT =  0x02
    T_LOW_LIMIT =   0x03
    EEPROM_UL =     0x04
    EEPROM1 =       0x05
    EEPROM2 =       0x06
    TEMP_OFFSET =   0x07
    EEPROM3 =       0x08
    ID =            0x0F

class AvgConversions(enum.IntEnum):
    avg_none =  0b00
    avg8 =      0b01
    avg32 =     0b10
    avg64 =     0b11

class ConversionCylceTime(enum.IntEnum):
    conv15p5ms =    0b000
    conv125ms =     0b001
    conv250ms =     0b010
    conv500ms =     0b011
    conv1s =        0b100
    conv4s =        0b101
    conv8s =        0b110
    conv16s =       0b111

class ConversionMode(enum.IntEnum):
    cc_mode =    0b00
    sd_mode =    0b01
    cc_mode2 =   0b10
    os_mode =    0b11

class TMP117:
    def __init__(self, ftdi_url='ftdi://ftdi:232h/1', addr=0x48):
        self.ctrl = pyftdi.i2c.I2cController()
        self.ctrl.configure(ftdi_url)
        self.dev = self.ctrl.get_port(addr)
        if self.get_device_id() != _DEVICE_ID:
            self.close()
            raise AttributeError('TMP117 not found!')

    def __into_two_bytes(self, data):
        split_two = struct.Struct('>h').pack
        byte1, byte2 = split_two(data)
        return [byte1, byte2]

    def __read_reg(self, reg, num_bytes=2):
        rd = struct.Struct('>h').unpack
        return rd(self.dev.read_from(reg, num_bytes))
    
    def __write_reg(self, reg, data):
        self.dev.write_to(reg, self.__into_two_bytes(data))

    def __convert_tempC(self, rawData):
        return rawData * _TEMP_CONVERSION_FACTOR  # rawData / 128

    def __convert_tempF(self, raw_data):
        tempC = raw_data * _TEMP_CONVERSION_FACTOR
        return tempC * _C_TO_F_CONVERSION_FACTOR + 32
    
    def __bit_write(self, data, bit, index):
        mask = 1 << index if bit else ~(1 << index)
        return data | mask if bit else data & mask
    
    def __bits_write(self, data, bits, msb, num_bits, data_size=16):
        # Replaces part of data with bits, starting at msb bit
        # num_bits should be number of bits in bits
        assert num_bits >= 0
        lsb = msb - (num_bits - 1)
        mask = (2**data_size - 1) - ((2**num_bits -1) << lsb)
        return (data & mask) | (bits << lsb)

    def __bit_read(self, data, index):
        mask = 1 << index
        return 1 if data & mask != 0 else 0

    def __bits_read(self, data, msb, num_bits):
        # reads chunk of num_bits >= 1
        assert num_bits >= 0
        out = 0
        lsb = msb - (num_bits - 1)
        for i in range(lsb, msb + 1):
            mask = 1 << i
            if data & mask != 0: out |= 1 << (i - lsb) 
        return out
    
    def __wait_while(self, wait_condition, msg, timeout=2.0, period=0.1):
        end_time = time.monotonic() + timeout
        while time.monotonic() < end_time:
            if not wait_condition:
                return True
            time.sleep(period)
        raise TimeoutError(msg)

    def read_tempC(self):
        raw_data = self.__read_reg(Reg.TEMP)
        tempC = self.__convert_tempC(raw_data[0])
        return tempC

    def read_tempF(self):
        raw_data = self.__read_reg(Reg.TEMP)
        tempF = self.__convert_tempF(raw_data[0])
        return tempF

    def get_device_id(self):
        return self.__read_reg(Reg.ID)[0]

    def get_config(self):
        return self.__read_reg(Reg.CFG)[0]
    
    def set_config(self, data):
        self.dev.write_to(Reg.CFG, data)

    def soft_reset(self):
        cfg_data = self.get_config()
        self.__write_reg(Reg.CFG, cfg_data | 0x02)
        self.__wait_while(self.is_eeprom_busy(), 'Software Reset timed out!')
    
    def is_data_ready(self):
        return self.__bit_read(self.get_config(), 13)

    def is_eeprom_busy(self):
        return self.__bit_read(self.get_config(), 12)
    

    def set_temp_high_limit(self, high_tempC):
        temp_count = high_tempC / _TEMP_CONVERSION_FACTOR
        reg_count = round(temp_count)
        self.__write_reg(Reg.T_HIGH_LIMIT, reg_count)
    
    def get_temp_high_limit(self):
        return self.__read_reg(Reg.T_HIGH_LIMIT)[0] * _TEMP_CONVERSION_FACTOR

    def set_temp_low_limit(self, low_tempC):
        temp_count = low_tempC / _TEMP_CONVERSION_FACTOR
        reg_count = round(temp_count)
        self.__write_reg(Reg.T_LOW_LIMIT, reg_count)
    
    def get_temp_low_limit(self):
        return self.__read_reg(Reg.T_LOW_LIMIT)[0] * _TEMP_CONVERSION_FACTOR
    
    def set_temp_offset(self, offset_tempC):
        temp_count = offset_tempC / _TEMP_CONVERSION_FACTOR
        reg_count = round(temp_count)
        self.__write_reg(Reg.TEMP_OFFSET, reg_count)
    
    def get_temp_offset(self):
        return self.__read_reg(Reg.TEMP_OFFSET)[0] * _TEMP_CONVERSION_FACTOR

    
    def get_high_low_alert(self):
        cfg = self.get_config()
        return self.__bits_read(cfg, 15, 2)
    
    def is_high_alert(self):
        return self.__bit_read(self.get_config(), 15)
    
    def is_low_alert(self):
        return self.__bit_read(self.get_config(), 14)

    def set_therm_alert(self, alert_on):
        cfg_data = self.get_config()
        self.__write_reg(Reg.CFG, self.__bit_write(cfg_data, alert_on, 4))

    def get_therm_alert(self):
        return self.__bit_read(self.get_config(), 4)

    def set_alert_polarity(self, polarity):
        cfg_data = self.get_config()
        self.__write_reg(Reg.CFG, self.__bit_write(cfg_data, polarity, 3))
    
    def get_alert_polarity(self):
        return self.__bit_read(self.get_config(), 3)

    def set_alert_pin(self, alert_pin):
        cfg_data = self.get_config()
        self.__write_reg(Reg.CFG, self.__bit_write(cfg_data, alert_pin, 2))
    
    def get_alert_pin(self):
        return self.__bit_read(self.get_config(), 2)

    
    def get_conversion_time(self):
        # returns conversion time in seconds
        cc_time = self.get_conversion_cycle_time()
        avg_conv = self.get_averaging()
        conv_table = ((15.5, 125, 500, 1000),
                        (125, 125, 500, 1000),
                        (250, 250, 500, 1000),
                        (500, 500, 500, 1000),
                        (1000, 1000, 1000, 1000),
                        (4000, 4000, 4000, 4000),
                        (8000, 8000, 8000, 8000),
                        (16000, 16000, 16000, 16000))
        return conv_table[cc_time][avg_conv]/1000
    
    def set_averaging(self, avg_select=AvgConversions.avg8):
        # avg_select can also simply be set to 0-3
        cfg = self.get_config()
        new_cfg = self.__bits_write(cfg, avg_select, 6, 2)
        self.__write_reg(Reg.CFG, new_cfg)
    
    def get_averaging(self):
        cfg = self.get_config()
        return self.__bits_read(cfg, 6, 2)
    
    def set_conversion_cycle_time(self, cc_time=ConversionCylceTime.conv1s):
        # cc_time can also simply be set to 0-7
        cfg = self.get_config()
        new_cfg = self.__bits_write(cfg, cc_time, 9, 3)
        self.__write_reg(Reg.CFG, new_cfg)
    
    def get_conversion_cycle_time(self):
        cfg = self.get_config()
        return self.__bits_read(cfg, 9, 3)
    
    def set_conversion_mode(self, mode=ConversionMode.cc_mode):
        # cc_time can also simply be set to 0-3
        cfg = self.get_config()
        new_cfg = self.__bits_write(cfg, mode, 11, 2)
        self.__write_reg(Reg.CFG, new_cfg)
    
    def get_conversion_mode(self):
        cfg = self.get_config()
        return self.__bits_read(cfg, 11, 2)

    def close(self):
        self.dev = None
        self.ctrl.terminate()
        self.ctrl = None
