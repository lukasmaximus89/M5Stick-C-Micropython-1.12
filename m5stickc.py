"""
m5stickc.py

High(?) level functions for dealing with M5StickC hardware

History:
    2019-12-27 TW created

"""

import sys

# workaround for micropython module caching
try:
    del sys.modules["axp192"]
except:
    pass

from machine import I2C, Pin
from axp192 import AXP192

hw_i2c_0 = I2C(0, sda=Pin(21), scl=Pin(22))
axp = AXP192(hw_i2c_0)
axp.setup()


def lcd_backlight_power(status=True):
    """Turn LCD backlight on or off"""

    # in M5StickC, LCD backlight is wired to AXP192 LD02 output.
    axp.set_LD02(status)


def power_button():
    """Returns status of the power button"""

    if axp.button():
        return True
    return False
