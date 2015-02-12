#####
from time import sleep
from time import time
import wiringpi2 as wiringpi
import signal
import os


class keyboard:

    def __init__(self, play_pin=3, eject_pin=5,
                 pwr_pin=7, choose_pin=11, rot_a=13,
                 rot_b=15, vol_a=21, vol_b=23):
        self.play_pin = play_pin
        self.eject_pin = eject_pin
        self.pwr_pin = pwr_pin

        self.choose_pin = choose_pin
        self.rot_a = rot_a
        self.rot_b = rot_b
        self.vol_a = vol_a
        self.vol_b = vol_b
        
        # setting pins to input mode

        wiringpi.wiringPiSetupPhys()
        wiringpi.pinMode(self.play_pin, 0)
        wiringpi.pinMode(self.eject_pin, 0)
        wiringpi.pinMode(self.pwr_pin, 0)
        wiringpi.pinMode(self.choose_pin, 0)
        wiringpi.pinMode(self.rot_a, 0)
        wiringpi.pinMode(self.rot_b, 0)
        wiringpi.pinMode(self.vol_a, 0)
        wiringpi.pinMode(self.vol_b, 0)
        
        # pulling them up
        
        wiringpi.pullUpDnControl(self.play_pin, 2)
        wiringpi.pullUpDnControl(self.eject_pin, 2)
        wiringpi.pullUpDnControl(self.pwr_pin, 2)
        wiringpi.pullUpDnControl(self.choose_pin, 2)
        wiringpi.pullUpDnControl(self.rot_a, 2)
        wiringpi.pullUpDnControl(self.rot_b, 2)
        wiringpi.pullUpDnControl(self.vol_a, 2)
        wiringpi.pullUpDnControl(self.vol_b, 2)

        
#        wiringpi.wiringPiISR(self.play_pin, 1, self.play_callback)
#        wiringpi.wiringPiISR(self.eject_pin, 1, self.eject_callback)
#        wiringpi.wiringPiISR(self.pwr_pin, 1, self.pwrbtn_callback)
#        wiringpi.wiringPiISR(self.choose_pin, 1, self.choice_callback)
#        wiringpi.wiringPiISR(self.rot_a, 1, self.rot_callback)
#        wiringpi.wiringPiISR(self.vol_a, 1, self.volp_callback)
#        wiringpi.wiringPiISR(self.vol_b, 1, self.volm_callback)
                              
        self.queue = ['']

        self.rot = 0
        self.oldrot = self.rot

    def play_callback(self):
        self.queue.append('play')
        os.kill(os.getpid(), signal.SIGUSR1)

    def eject_callback(self):
        self.queue.append('eject')
        os.kill(os.getpid(), signal.SIGUSR1)

    def pwrbtn_callback(self):
        self.queue.append('pwr')
        os.kill(os.getpid(), signal.SIGUSR1)

    def choice_callback(self):
        self.queue.append('enter')
        os.kill(os.getpid(), signal.SIGUSR1)

    def rot_callback(self):
        if wiringpi.digitalRead(self.rot_a) == \
                            wiringpi.digitalRead(self.rot_b):
            self.rot += 1
        else:
            self.rot -= 1
        r = self.rot/2

        if r != self.oldrot:
            delta = r - self.oldrot
            self.oldrot = r
            if delta > 0:
                self.queue.append('fwd')
            else:
                self.queue.append('back')
            os.kill(os.getpid(), signal.SIGUSR1)

    def volp_callback(self):
        self.queue.append('vol+')
        os.kill(os.getpid(), signal.SIGUSR1)

    def volm_callback(self):
        self.queue.append('vol-')
        os.kill(os.getpid(), signal.SIGUSR1)
        
    def cln(self):
        wiringpi.pullUpDnControl(self.play_pin, 0)
        wiringpi.pullUpDnControl(self.eject_pin, 0)
        wiringpi.pullUpDnControl(self.pwr_pin, 0)
        wiringpi.pullUpDnControl(self.choose_pin, 0)
        wiringpi.pullUpDnControl(self.rot_a, 0)
        wiringpi.pullUpDnControl(self.rot_b, 0)
        wiringpi.pullUpDnControl(self.vol_a, 0)
        wiringpi.pullUpDnControl(self.vol_b, 0)
