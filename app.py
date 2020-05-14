"""
app.py
"""

import sys
import time


def run():
    # workaround micropython module cache
    try:
        del sys.modules["m5stickc"]
    except:
        pass

    try:
        from m5stickc import lcd_backlight_power, power_button, axp

        lcd_backlight_power(True)
        time.sleep(1)
        lcd_backlight_power(False)
        print("Battery Voltage: {}".format(axp.battery_voltage()))
        print("Battery Current: {}".format(axp.battery_current()))
        print("Bus Voltage: {}".format(axp.bus_voltage()))
        print("Bus Current: {}".format(axp.bus_current()))
        print("Input Voltage: {}".format(axp.input_voltage()))
        print("Input Current: {}".format(axp.input_current()))
        print("Temperature: {}".format(axp.temperature()))
        print("Batt power: {}".format(axp.battery_power()))
        print("Batt charge current: {}".format(axp.battery_charge_current()))
        print("APS Voltage: {}".format(axp.aps_voltage()))
        print("warning_level: {}".format(axp.warning_level()))

    #    while True:
    #        print("power button: {}".format(power_button()))
    #        time.sleep_ms(100)
    except Exception as e:
        sys.print_exception(e)
        del sys.modules["m5stickc"]
        del sys.modules[__name__]


if __name__ == "__main__":
    run()
