""" Module for interfacing with LCD 16x2 based on HD44780 """
import RPi.GPIO as GPIO
from time import sleep


class HD44780(object):
    """ Main class for LCD """

    def __init__(self, pin_rs=12, pin_e=11, pins_db=None):
        """ Initializing LCD """
        self.pin_rs = pin_rs
        self.pin_e = pin_e
        if pins_db is None:
            self.pins_db = [5, 7, 10, 3]
        else:
            self.pins_db = pins_db

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pin_e, GPIO.OUT)
        GPIO.setup(self.pin_rs, GPIO.OUT)
        for pin in self.pins_db:
            GPIO.setup(pin, GPIO.OUT)

        self.clear()

    def clear(self):
        """ Blank / Reset LCD """

        self.cmd(0x33)  # $33 8-bit mode
        self.cmd(0x32)  # $32 8-bit mode
        self.cmd(0x28)  # $28 8-bit mode
        self.cmd(0x0C)  # $0C 8-bit mode
        self.cmd(0x06)  # $06 8-bit mode
        self.cmd(0x01)  # $01 8-bit mode

    def cmd(self, bits, char_mode=False):
        """ Send command to LCD """

        sleep(0.001)
        bits = bin(bits)[2:].zfill(8)

        GPIO.output(self.pin_rs, char_mode)

        for pin in self.pins_db:
            GPIO.output(pin, False)

        for i in range(4):
            if bits[i] == "1":
                GPIO.output(self.pins_db[::-1][i], True)

        GPIO.output(self.pin_e, True)
        GPIO.output(self.pin_e, False)

        for pin in self.pins_db:
            GPIO.output(pin, False)

        for i in range(4, 8):
            if bits[i] == "1":
                GPIO.output(self.pins_db[::-1][i-4], True)

        GPIO.output(self.pin_e, True)
        GPIO.output(self.pin_e, False)

    def message(self, text):
        """ Send string to LCD. Newline wraps to second line"""
        self.cmd(0x02)  # return home
        for char in text:
            if char == '\n':
                self.cmd(0xC0)  # next line
            else:
                self.cmd(ord(char), True)
