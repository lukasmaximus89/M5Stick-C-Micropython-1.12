"""
Driver for AXP192, as used in the M5StickC.

As I was not able to find a non-chinese data sheet of the AXP192, the
adresses and functions here are mostly copied from the Arduino library
on https://github.com/m5stack/M5StickC/blob/master/src/AXP192.cpp.

History:
    2019-12-27 TW created

"""


AXP192_I2C_ADDRESS = 0x34


class AXP192_Conf:
    """Configuration of important AXP192 outputs"""

    def __init__(self, LD02=True, LD03=True, RTC=True, DCDC1=True, DCDC3=True):
        self.LD02 = LD02
        self.LD03 = LD03
        self.RTC = RTC
        self.DCDC1 = DCDC1
        self.DCDC3 = DCDC3

    def mask_0x12(self):
        m = 0
        if self.LD03:
            m |= (1 << 3)
        if self.LD02:
            m |= (1 << 2)
        if self.DCDC3:
            m |= (1 << 1)
        if self.DCDC1:
            m |= (1 << 0)
        return m

    def set_LD02(self, status):
        self.LD02 = status


class AXP192:
    """AXP192: Initialization and Interface.

    Stolen from https://github.com/m5stack/M5StickC
    """

    def __init__(self, i2c_bus):
        self.i2c = i2c_bus
        self.conf = AXP192_Conf()

    def _write(self, addr, *values):
        b = bytearray(1)
        b[0] = values[0]
        self.i2c.writeto_mem(AXP192_I2C_ADDRESS, addr, b)

    def _read(self, addr, nbytes=1):
        return self.i2c.readfrom_mem(AXP192_I2C_ADDRESS, addr, nbytes)

    def _read_bits(self, addr, nbits):
        """Read values from AXP192 and decode partial bytes"""

        nbytes = int(nbits / 8)
        if (nbits % 8) != 0:
            nbytes += 1

        b = self._read(addr, nbytes)

        # decoding partial bytes:
        #   relevant bits of the partial bytes seem to be in the high bits
        #   of the first byte.
        #   C Source:
        #       Data = ((buf[0] << 4) + buf[1])
        ret = 0
        # partial bytes
        if (nbits % 8) == 0:
            # MSB first, LSB last
            for byte in b:
                ret = (ret << 8) | byte
        elif nbits == 12:
            ret = (b[0] << 4) | b[1]
        elif nbits == 13:
            ret = (b[0] << 5) | b[1]
        else:
            raise Exception("invalid number of bits")

        return ret

    def setup(self):
        """Initialize AXP192 with defaults for the M5StickC

        Arduino call: begin()
        """

        # Set LDO2 & LDO3(TFT_LED & TFT) 3.0V
        self._write(0x28, 0xcc)

        # Set ADC sample rate to 200hz
        self._write(0x84, int("0b11110010"))

        # Set ADC to All Enable
        self._write(0x82, 0xff)

        # Bat charge voltage to 4.2, Current 100MA
        self._write(0x33, 0xc0)

        # Depending on configuration enable LDO2, LDO3, DCDC1, DCDC3.
        self._set_power_0x12()

        # 128ms power on, 4s power off
        self._write(0x36, 0x0C)

        if self.conf.RTC:  # RTC enabled
            # Set RTC voltage to 3.3V
            self._write(0x91, 0xF0)

            # Set GPIO0 to LDO
            self._write(0x90, 0x02)

        # Disable vbus hold limit
        self._write(0x30, 0x80)

        # Set temperature protection
        self._write(0x39, 0xfc)

        # Enable RTC BAT charge
        tmp = 0x7f
        if self.conf.RTC:
            tmp = 0xff
        self._write(0x35, 0xa2 & tmp)

        # Enable bat detection
        self._write(0x32, 0x46)

    # Depending on configuration enable LDO2, LDO3, DCDC1, DCDC3.
    def _set_power_0x12(self):
        b = (self._read_bits(0x12, 8) & 0xef) | 0x4D
        b = (b & 0xf0) | self.conf.mask_0x12()
        self._write(0x12, b)

    def set_LD02(self, status):
        """Turn LD02 output on or off.

        On M5StickC, this is connected to the LCD backlight.

        Arduino call: SetLDO2()
        """

        self.conf.LD02 = status
        self._set_power_0x12()

    def button(self):
        """Return status of the M5StickC power button

        Arduino call: GetBtnPress()
        """
        st = self._read_bits(0x46, 8)
        if st:
            self._write(0x46, 0x03)
        return st

    def battery_voltage(self):
        """Return battery voltage

        Arduino call: GetBatVoltage()
        """
        ADCLSB = 1.1 / 1000.0
        return ADCLSB * self._read_bits(0x78, 12)

    def battery_current(self):
        """Return battery current

        Arduino call: GetBatCurrent()
        """
        ADCLSB = 0.5
        a_in = self._read_bits(0x7a, 13)    # current to battery ?
        a_out = self._read_bits(0x7c, 13)   # current from battery ?
        return ADCLSB * (a_in - a_out)

    def input_voltage(self):
        """Return input voltage.

        This returns 0V always (?)

        Arduino call: GetVinVoltage()
        """
        ADCLSB = 1.7 / 1000.0
        return ADCLSB * self._read_bits(0x56, 12)

    def input_current(self):
        """Return input current.

        This returns 0A always (?)

        Arduino call: GetVinCurrent()
        """
        ADCLSB = 0.625
        return ADCLSB * self._read_bits(0x58, 12)

    def bus_voltage(self):
        """Return bus voltage.

        Arduino call: GetVBusVoltage()
        """
        ADCLSB = 1.7 / 1000.0
        return ADCLSB * self._read_bits(0x5a, 12)

    def bus_current(self):
        """Return bus current.

        Not sure if this is correct, as my M5StickC reports only 30mA here.

        Arduino call: GetVBusCurrent()
        """
        ADCLSB = 0.375
        return ADCLSB * self._read_bits(0x5c, 12)

    def temperature(self):
        """Return AXP192 temperature in °C.

        Arduino call: GetTempInAXP192()
        """
        ADCLSB = 0.1
        OFFSET_DEG_C = -144.7
        return OFFSET_DEG_C + ADCLSB * self._read_bits(0x5e, 12)

    def battery_power(self):
        """Return information about battery state(?)

        Arduino call: GetBatPower()
        """
        VoltageLSB = 1.1
        CurrentLCS = 0.5
        return VoltageLSB * CurrentLCS * self._read_bits(0x70, 24)

    def battery_charge_current(self):
        """Return current flowing into the battery.

        Arduino call: GetBatChargeCurrent()
        """
        ADCLSB = 0.5
        # Why do we read 12 bits here and 13 bits in battery_current()
        # above ?
        return ADCLSB * self._read_bits(0x7a, 12)

    def aps_voltage(self):
        """Return APS voltage. No Idea what this is.

        Arduino call: GetAPSVoltage()
        """
        ADCLSB = 1.4 / 1000.0
        return ADCLSB * self._read_bits(0x7e, 12)

    def warning_level(self):
        """Most likely warns about battery low (?)

        Arduino call: GetWarningLevel()
        """
        if self._read_bits(0x47, 8) & 0x01:
            return True
        return False

    def set_sleep(self):
        """Turn off most power outputs.

        Arduino call: SetSleep()
        """
        buf = self._read_bits(0x31, 8)
        buf = (1 << 3) | buf
        self._write(0x31, buf)       # no idea what this does
        self._write(0x90, 0x00)      # GPIO 0 not longer on LD0
        self._write(0x12, 0x09)
        self._write(0x12, 0x00)      # disable LD02, LD03, DCDC1, DCDC3
