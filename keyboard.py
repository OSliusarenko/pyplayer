#####
import RPi.GPIO as GPIO
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

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.play_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.eject_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.pwr_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.choose_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.rot_a, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.rot_b, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.vol_a, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.vol_b, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        GPIO.add_event_detect(self.play_pin, GPIO.FALLING,
                              callback=self.play_callback, bouncetime=200)
        GPIO.add_event_detect(self.eject_pin, GPIO.FALLING,
                              callback=self.eject_callback, bouncetime=200)
        GPIO.add_event_detect(self.pwr_pin, GPIO.FALLING,
                              callback=self.pwrbtn_callback, bouncetime=200)
        GPIO.add_event_detect(self.choose_pin, GPIO.FALLING,
                              callback=self.choice_callback, bouncetime=200)
        GPIO.add_event_detect(self.rot_a, GPIO.FALLING,
                              callback=self.rot_callback, bouncetime=5)
        GPIO.add_event_detect(self.vol_a, GPIO.FALLING,
                              callback=self.volp_callback, bouncetime=5)
        GPIO.add_event_detect(self.vol_b, GPIO.FALLING,
                              callback=self.volm_callback, bouncetime=5)

        self.queue = ['']

        self.rot = 0
        self.oldrot = self.rot

    def play_callback(self, channel):
        self.queue.append('play')
        os.kill(os.getpid(), signal.SIGUSR1)

    def eject_callback(self, channel):
        self.queue.append('eject')
        os.kill(os.getpid(), signal.SIGUSR1)

    def pwrbtn_callback(self, channel):
        self.queue.append('pwr')
        os.kill(os.getpid(), signal.SIGUSR1)

    def choice_callback(self, channel):
        self.queue.append('enter')
        os.kill(os.getpid(), signal.SIGUSR1)

    def rot_callback(self, channel):
        if GPIO.input(self.rot_a) == GPIO.input(self.rot_b):
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

    def volp_callback(self, channel):
        self.queue.append('vol+')
        os.kill(os.getpid(), signal.SIGUSR1)

    def volm_callback(self, channel):
        self.queue.append('vol-')
        os.kill(os.getpid(), signal.SIGUSR1)
