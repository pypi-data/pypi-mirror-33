# Copyright 2015 Nick Lee
# Copyright 2014 IIJ Innovation Institute Inc. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY IIJ INNOVATION INSTITUTE INC. ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL IIJ INNOVATION INSTITUTE INC. OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


# Copyright 2014 Keiichi Shima. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import time
import threading

__all__ = ['util', 'DS18B20', 'BMP180', 'HTU21D', 'MCP3004', 'LCD1602']

# Locks for buses: subclasses of SensorBase should apply the appropriate
# decorator(s) to ensure only one device is accessing a particular bus
# at any given moment.

_w1_lock = threading.Lock()

def w1_lock(func):
    def locked(*args, **kwargs):
        with _w1_lock:
            func(*args, **kwargs)
    return locked

_i2c_lock = threading.Lock()

def i2c_lock(func):
    def locked(*args, **kwargs):
        with _i2c_lock:
            func(*args, **kwargs)
    return locked

_spi_lock = threading.Lock()

def spi_lock(func):
    def locked(*args, **kwargs):
        with _spi_lock:
            func(*args, **kwargs)
    return locked

class SensorBase(object):
    def __init__(self, update_callback):
        assert (update_callback is not None)

        self._cache_lifetime = 0
        self._last_updated = None
        self._update_callback = update_callback

    def _update(self, **kwargs):
        now = time.time()

        # If caching is disabled, just update the data.
        if self._cache_lifetime > 0:
            # Check if the cached value is still valid or not.
            if (self._last_updated is not None
                and self._last_updated + self._cache_lifetime > now):
                # The value is still valid.
                return

        # Get the latest sensor values.
        try:
            self._update_callback(**kwargs)
            self._last_updated = now
        except:
            raise

        return

    @property
    def cache_lifetime(self):
        '''Gets/Sets the cache time (in seconds).
        '''
        return (self._cache_lifetime)

    @cache_lifetime.setter
    def cache_lifetime(self, cache_lifetime):
        assert(cache_lifetime >= 0)

        self._cache_lifetime = cache_lifetime


""" LCD Stuff
Downloaded and adapted from:
  http://www.imediabank.com/download/sankilcd.tar.gz
"""

import smbus

class i2c_device:
    def __init__(self, addr, port):
        self.addr = addr
        self.bus = smbus.SMBus(port)

    # Write a single command
    def write_cmd(self, cmd):
        self.bus.write_byte(self.addr, cmd)
        time.sleep(0.0001)

    # Write a command and argument
    def write_cmd_arg(self, cmd, data):
        self.bus.write_byte_data(self.addr, cmd, data)
        time.sleep(0.0001)

    # Write a block of data
    def write_block_data(self, cmd, data):
        self.bus.write_block_data(self.addr, cmd, data)
        time.sleep(0.0001)

    # Read a single byte
    def read(self):
        return self.bus.read_byte(self.addr)

    # Read
    def read_data(self, cmd):
        return self.bus.read_byte_data(self.addr, cmd)

    # Read a block of data
    def read_block_data(self, cmd):
        return self.bus.read_block_data(self.addr, cmd)


# commands
LCD_CLEARDISPLAY = 0x01
LCD_RETURNHOME = 0x02
LCD_ENTRYMODESET = 0x04
LCD_DISPLAYCONTROL = 0x08
LCD_CURSORSHIFT = 0x10
LCD_FUNCTIONSET = 0x20
LCD_SETCGRAMADDR = 0x40
LCD_SETDDRAMADDR = 0x80

# flags for display entry mode
LCD_ENTRYRIGHT = 0x00
LCD_ENTRYLEFT = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00

# flags for display on/off control
LCD_DISPLAYON = 0x04
LCD_DISPLAYOFF = 0x00
LCD_CURSORON = 0x02
LCD_CURSOROFF = 0x00
LCD_BLINKON = 0x01
LCD_BLINKOFF = 0x00

# flags for display/cursor shift
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE = 0x00
LCD_MOVERIGHT = 0x04
LCD_MOVELEFT = 0x00

# flags for function set
LCD_8BITMODE = 0x10
LCD_4BITMODE = 0x00
LCD_2LINE = 0x08
LCD_1LINE = 0x00
LCD_5x10DOTS = 0x04
LCD_5x8DOTS = 0x00

# flags for backlight control
LCD_BACKLIGHT = 0x08
LCD_NOBACKLIGHT = 0x00
En = 0b00000100 # Enable bit
Rw = 0b00000010 # Read/Write bit
Rs = 0b00000001 # Register select bit

class LCDBase(object):
    # To be filled in by subclass
    LINE_LENGTH = None

    #initializes objects and lcd
    def __init__(self, bus, addr):
        self._lcd_device = i2c_device(addr, bus)
        self._write(0x03)
        self._write(0x03)
        self._write(0x03)
        self._write(0x02)
        self._write(LCD_FUNCTIONSET | LCD_2LINE | LCD_5x8DOTS | LCD_4BITMODE)
        self._write(LCD_DISPLAYCONTROL | LCD_DISPLAYON)
        self._write(LCD_ENTRYMODESET | LCD_ENTRYLEFT)
        time.sleep(0.2)

    # clocks EN to latch command
    def _strobe(self, data):
        self._lcd_device.write_cmd(data | En | LCD_BACKLIGHT)
        time.sleep(.0005)
        self._lcd_device.write_cmd(((data & ~En) | LCD_BACKLIGHT))
        time.sleep(.0001)

    def _write_four_bits(self, data):
        self._lcd_device.write_cmd(data | LCD_BACKLIGHT)
        self._strobe(data)

    # write a command to lcd
    def _write(self, cmd, mode=0):
        self._write_four_bits(mode | (cmd & 0xF0))
        self._write_four_bits(mode | ((cmd << 4) & 0xF0))

    # put string function
    @i2c_lock
    def display(self, string, line):
        # ensure line length
        string = string.ljust(self.LINE_LENGTH)[:self.LINE_LENGTH]

        if line == 1:
            self._write(0x80)
        if line == 2:
            self._write(0xC0)
        if line == 3:
            self._write(0x94)
        if line == 4:
            self._write(0xD4)

        for char in string:
            self._write(ord(char), Rs)

    # clear lcd and set to home
    @i2c_lock
    def clear(self):
        self._write(LCD_CLEARDISPLAY)
        self._write(LCD_RETURNHOME)
