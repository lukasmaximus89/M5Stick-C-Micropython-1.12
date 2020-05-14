# C.LEBOCQ 02/2020
# MicroPython library for the MPU6886 imu ( M5StickC / ATOM Matrix ) 
# Based on https://github.com/m5stack/M5StickC/blob/master/src/utility/MPU6886.cpp

from machine import I2C
from time import sleep

MPU6886_ADDRESS           = const(0x68)
MPU6886_WHOAMI            = const(0x75)
MPU6886_ACCEL_INTEL_CTRL  = const(0x69)
MPU6886_SMPLRT_DIV        = const(0x19)
MPU6886_INT_PIN_CFG       = const(0x37)
MPU6886_INT_ENABLE        = const(0x38)
MPU6886_ACCEL_XOUT_H      = const(0x3B)
MPU6886_ACCEL_XOUT_L      = const(0x3C)
MPU6886_ACCEL_YOUT_H      = const(0x3D)
MPU6886_ACCEL_YOUT_L      = const(0x3E)
MPU6886_ACCEL_ZOUT_H      = const(0x3F)
MPU6886_ACCEL_ZOUT_L      = const(0x40)

MPU6886_TEMP_OUT_H        = const(0x41)
MPU6886_TEMP_OUT_L        = const(0x42)

MPU6886_GYRO_XOUT_H       = const(0x43)
MPU6886_GYRO_XOUT_L       = const(0x44)
MPU6886_GYRO_YOUT_H       = const(0x45)
MPU6886_GYRO_YOUT_L       = const(0x46)
MPU6886_GYRO_ZOUT_H       = const(0x47)
MPU6886_GYRO_ZOUT_L       = const(0x48)

MPU6886_USER_CTRL         = const(0x6A)
MPU6886_PWR_MGMT_1        = const(0x6B)
MPU6886_PWR_MGMT_2        = const(0x6C)
MPU6886_CONFIG            = const(0x1A)
MPU6886_GYRO_CONFIG       = const(0x1B)
MPU6886_ACCEL_CONFIG      = const(0x1C)
MPU6886_ACCEL_CONFIG2     = const(0x1D)
MPU6886_FIFO_EN           = const(0x23)

#consts for Acceleration & Resolution scale
AFS_2G      = const(0x00)
AFS_4G      = const(0x01)
AFS_8G      = const(0x02)
AFS_16G     = const(0x03)

GFS_250DPS  = const(0x00)
GFS_500DPS  = const(0x01)
GFS_1000DPS = const(0x02)
GFS_2000DPS = const(0x03)

class MPU6886():

    def __init__(self, i2c, Gscale = GFS_2000DPS, Ascale = AFS_8G):
        self.i2c = i2c
        self.Gscale = Gscale
        self.Ascale = Ascale
        if self.init():
            self.setAccelFsr(Ascale)
            self.setGyroFsr(Gscale)

    # sleep in ms
    def sleepms(self,n):
        sleep(n / 1000)
    
    # set I2C reg (1 byte)
    def	setReg(self, reg, dat):
        self.i2c.writeto(MPU6886_ADDRESS, bytearray([reg, dat]))
		
    # get I2C reg (1 byte)
    def	getReg(self, reg):
        self.i2c.writeto(MPU6886_ADDRESS, bytearray([reg]))
        t =	self.i2c.readfrom(MPU6886_ADDRESS, 1)
        return t[0]

    # get n reg
    def	getnReg(self, reg, n):
        self.i2c.writeto(MPU6886_ADDRESS, bytearray([reg]))
        t =	self.i2c.readfrom(MPU6886_ADDRESS, n)
        return t    

    def init(self):
        tempdata = self.getReg(MPU6886_WHOAMI)
        if tempdata != 0x19:
            return False
        self.sleepms(1)
        regdata = 0x00
        self.setReg(MPU6886_PWR_MGMT_1, regdata)
        self.sleepms(10)      
        regdata = (0x01<<7)
        self.setReg(MPU6886_PWR_MGMT_1, regdata)
        self.sleepms(10)
        regdata = (0x01<<0)
        self.setReg(MPU6886_PWR_MGMT_1, regdata)
        self.sleepms(10)
        regdata = 0x10
        self.setReg(MPU6886_ACCEL_CONFIG, regdata)
        self.sleepms(1)
        regdata = 0x18
        self.setReg(MPU6886_GYRO_CONFIG, regdata)
        self.sleepms(1)
        regdata = 0x01
        self.setReg(MPU6886_CONFIG, regdata)
        self.sleepms(1)
        regdata = 0x05
        self.setReg(MPU6886_SMPLRT_DIV, regdata)
        self.sleepms(1)
        regdata = 0x00
        self.setReg(MPU6886_INT_ENABLE, regdata)
        self.sleepms(1)
        regdata = 0x00
        self.setReg(MPU6886_ACCEL_CONFIG2, regdata)
        self.sleepms(1)
        regdata = 0x00
        self.setReg(MPU6886_USER_CTRL, regdata)
        self.sleepms(1)
        regdata = 0x00
        self.setReg(MPU6886_FIFO_EN, regdata)
        self.sleepms(1)
        regdata = 0x22
        self.setReg(MPU6886_INT_PIN_CFG, regdata)
        self.sleepms(1)
        regdata = 0x01
        self.setReg(MPU6886_INT_ENABLE, regdata)
        self.sleepms(100)
        self.getGres()
        self.getAres()
        return True      

    def getGres(self):
        if self.Gscale == GFS_250DPS:
            self.gRes = 250.0 / 32768.0
        elif self.Gscale == GFS_500DPS:
            self.gRes = 500.0/32768.0
        elif self.Gscale == GFS_1000DPS:
            self.gRes = 1000.0/32768.0
        elif self.Gscale == GFS_2000DPS:
            self.gRes = 2000.0/32768.0
        else:
            self.gRes = 250.0/32768.0

    def getAres(self):
        if self.Ascale == AFS_2G:
            self.aRes = 2.0/32768.0
        elif self.Ascale == AFS_4G:
            self.aRes = 4.0/32768.0
        elif self.Ascale == AFS_8G: 
            self.aRes = 8.0/32768.0
        elif self.Ascale == AFS_16G:
            self.aRes = 16.0/32768.0
        else:
            self.aRes = 2.0/32768.0

    def getAccelAdc(self):
        buf = self.getnReg(MPU6886_ACCEL_XOUT_H,6)
                   
        ax = (buf[0]<<8) | buf[1]
        ay = (buf[2]<<8) | buf[3]
        az = (buf[4]<<8) | buf[5]
        return ax,ay,az

    def getAccelData(self):
        ax,ay,az = self.getAccelAdc()
        if ax > 32768:
            ax -= 65536
        if ay > 32768:
            ay -= 65536
        if az > 32768:
            az -= 65536
        ax *=  self.aRes
        ay *=  self.aRes
        az *=  self.aRes
        return ax,ay,az

    def getGyroAdc(self):
        buf = self.getnReg(MPU6886_GYRO_XOUT_H,6)
        gx = (buf[0]<<8) | buf[1]  
        gy = (buf[2]<<8) | buf[3]  
        gz = (buf[4]<<8) | buf[5]
        return gx,gy,gz

    def getGyroData(self):
        gx,gy,gz = self.getGyroAdc()
        if gx > 32768:
            gx -= 65536
        if gy > 32768:
            gy -= 65536
        if gz > 32768:
            gz -= 65536 
        gx *= self.gRes
        gy *= self.gRes
        gz *= self.gRes
        return gx, gy, gz 

    def getTempAdc(self):
        buf = self.getnReg(MPU6886_TEMP_OUT_H,2)
        return (buf[0]<<8) | buf[1]  

    def getTempData(self):
        return self.getTempAdc() / 326.8 + 25.0

    def setGyroFsr(self,scale):
        regdata = (scale<<3)
        self.setReg(MPU6886_GYRO_CONFIG, regdata)
        self.sleepms(10)
        self.Gscale = scale
        self.getGres()

    def setAccelFsr(self,scale):
        regdata = (scale<<3)
        self.setReg(MPU6886_ACCEL_CONFIG, regdata)
        self.sleepms(10)
        self.Ascale = scale
        self.getAres()