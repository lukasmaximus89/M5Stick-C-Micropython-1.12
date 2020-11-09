import framebuf
import time
from machine import Pin, SPI, I2C
from axp192 import AXP192

'''
import m5stickc_lcd
lcd = m5stickc_lcd.ST7735()
lcd.text('hello', 10, 10, 0xffff)
lcd.show()
'''


class ST7735(framebuf.FrameBuffer):
    def __init__(self):
        self.baudrate = 27000000
        self.cs = Pin(5, Pin.OUT, value=1)
        self.dc = Pin(23, Pin.OUT, value=1)
        self.rst = Pin(18, Pin.OUT, value=1)
        self.spi = SPI(
                1, baudrate=self.baudrate,
                polarity=0, phase=0, bits=8, firstbit=SPI.MSB,
                sck=Pin(13), mosi=Pin(15))

        self.enable_lcd_power()

        self.rst.on()
        time.sleep_ms(5)
        self.rst.off()
        time.sleep_ms(20)
        self.rst.on()
        time.sleep_ms(150)

        self.width = 80
        self.height = 160
        self.buffer = bytearray(self.width * self.height * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        self.init_display()

    def enable_lcd_power(self):
        i2c = I2C(0, sda=Pin(21), scl=Pin(22))
        axp = AXP192(i2c)
        axp.setup()
        axp.set_LD02(True)

    def init_display(self):
        for cmd, data, delay in [
            (0x01, None, 150),
            (0x11, None, 500),
            (0xb1, b'\x01\x2c\x2d', None),
            (0xb2, b'\x01\x2c\x2d', None),
            (0xb3, b'\x01\x2c\x2d\x01\x2c\x2d', None),
            (0xb4, b'\x07', None),
            (0xc0, b'\xa2\x02\x84', None),
            (0xc1, b'\xc5', None),
            (0xc2, b'\x0a\x00', None),
            (0xc3, b'\x8a\x2a', None),
            (0xc4, b'\x8a\xee', None),
            (0xc5, b'\x0e', None),
            (0x20, None, None),
            (0x36, b'\xc8', None),
            (0x3a, b'\x05', None),
            (0x2a, b'\x00\x02\x00\x81', None),
            (0x2b, b'\x00\x01\x00\xa0', None),
            (0x21, None, None),
            (0xe0, b'\x02\x1c\x07\x12\x37\x32\x29\x2d\x29\x25\x2b\x39\x00\x01\x03\x10', None),
            (0xe1, b'\x03\x1d\x07\x06\x2e\x2c\x29\x2d\x2e\x2e\x37\x3f\x00\x00\x02\x10', None),
            (0x13, None, 10),
            (0x29, None, 100),
            (0x36, b'\xcc', 10),
        ]:
            self.write_cmd(cmd)
            if data:
                self.write_data(data)
            if delay:
                time.sleep_ms(delay)
        self.fill(0)
        self.show()

    def show(self):
        self.write_cmd(0x2a)
        self.write_data(b'\x00\x1a\x00\x69')
        self.write_cmd(0x2b)
        self.write_data(b'\x00\x01\x00\xa0')
        self.write_cmd(0x2c)
        self.write_data(self.buffer)

    def write_cmd(self, cmd):
        self.dc.off()
        self.cs.off()
        self.spi.write(bytes([cmd]))
        self.cs.on()

    def write_data(self, buf):
        self.dc.on()
        self.cs.off()
        self.spi.write(buf)
        self.cs.on()
