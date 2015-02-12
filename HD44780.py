import wiringpi2 as wiringpi
from time import sleep


class HD44780:

    def __init__(self, pin_rs=26, pin_e=24, pins_db=[22, 18, 16, 12]):

        self.pin_rs = pin_rs
        self.pin_e = pin_e
        self.pins_db = pins_db

        wiringpi.wiringPiSetupPhys()
        wiringpi.pinMode(self.pin_e, 1)
        wiringpi.pinMode(self.pin_rs, 1)
        for pin in self.pins_db:
            wiringpi.pinMode(pin, 1)

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

        wiringpi.digitalWrite(self.pin_rs, char_mode)

        for pin in self.pins_db:
            wiringpi.digitalWrite(pin, False)

        for i in range(4):
            if bits[i] == "1":
                wiringpi.digitalWrite(self.pins_db[::-1][i], True)

        wiringpi.digitalWrite(self.pin_e, True)
        wiringpi.digitalWrite(self.pin_e, False)

        for pin in self.pins_db:
            wiringpi.digitalWrite(pin, False)

        for i in range(4, 8):
            if bits[i] == "1":
                wiringpi.digitalWrite(self.pins_db[::-1][i-4], True)

        wiringpi.digitalWrite(self.pin_e, True)
        wiringpi.digitalWrite(self.pin_e, False)

    def message(self, text):
        """ Send string to LCD. Newline wraps to second line"""
        self.cmd(0x02)  # return home
        for char in text:
            if char == '\n':
                self.cmd(0xC0)  # next line
            else:
                self.cmd(ord(char), True)
    
    def cln(self):
        wiringpi.digitalWrite(self.pin_e, 0)
        wiringpi.pinMode(self.pin_e, 0)
        wiringpi.digitalWrite(self.pin_rs, 0)
        wiringpi.pinMode(self.pin_rs, 0)
        for pin in self.pins_db:
            wiringpi.digitalWrite(pin, 0)
            wiringpi.pinMode(pin, 0)        
