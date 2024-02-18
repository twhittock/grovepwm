#!/usr/bin/env python
import smbus2
import time
from enum import IntEnum
import logging
from typing import Tuple

_LOG = logging.getLogger("grovepwm")

class Frequency(IntEnum):
    F_31372Hz = 0x01
    F_3921Hz = 0x02
    F_490Hz = 0x03
    F_122Hz = 0x04
    F_30Hz = 0x05

class _Registers(IntEnum):
    Frequency = 0x84
    Direction = 0xAA
    Speed = 0x82

class PWMDriver:
    "Driver compatible with seeed's I2C Motor Driver v1.3"
    def __init__(self, i2c_bus=1, addr=0x0f):
        self.bus = smbus2.SMBus(i2c_bus)
        time.sleep(0.01) # Ensure board has initialised
        self.addr = addr
        self.setFrequency(Frequency.F_3921Hz)

    def __del__(self):
        "Ensure the PWM is off once the driver exits"
        _LOG.debug("Driver destroyed - stopping PWM")
        self.setSpeed(0, 0)

    def _write(self, reg : _Registers, data : Tuple[int, int]):
        _LOG.debug("Setting addr: 0x%02x, reg: %s, data: %r", self.addr, reg.name, data)
        self.bus.write_i2c_block_data(self.addr, int(reg), data)

    def setFrequency(self, freq : Frequency):
        """Set the frequency to one of the predefined frequency values.
        This can change the response of different PWM-controlled devices"""
        self._write(_Registers.Frequency, (int(freq), 1))

    def setSpeed(self, speed_1 : float, speed_2 : float):
        """Set the speed of motors 1 and 2, -1 to +1 floating point.
        Calling too quickly will cause IO errors, so ensure calls are spaced out."""
        direction = \
                (1 if speed_1 < 0 else 2) + \
                (4 if speed_2 < 0 else 8)
        self._write(_Registers.Direction, (direction, 1))
        def floatToByte(f):
            return int(round(abs(f) * 255))
        self._write(_Registers.Speed, (floatToByte(speed_1), floatToByte(speed_2)))

def main():
    "Test function - cycle motors through -1 to +1 speed in a sine wave"
    import math

    logging.basicConfig(level=logging.INFO)
    testLog = logging.getLogger('test')

    driver = PWMDriver()
    testLog.info("Created driver - test cycling")
    totalTime = 4
    startTime = time.time()
    currentTime = time.time()
    while currentTime < (startTime + totalTime):
        spd = math.sin((currentTime - startTime) / totalTime * math.pi * 2)
        testLog.info("Speed %g", spd)
        driver.setSpeed(spd, spd)
        currentTime = time.time()
        time.sleep(0.015)
    driver.setSpeed(0, 0)
    testLog.info("Done - stopped motor")

if __name__ == '__main__':
    main()
