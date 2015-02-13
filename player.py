#!/usr/bin/python

import os
import signal
import locale
import subprocess
import RPi.GPIO as GPIO
import sys
from HD44780 import HD44780
from keyboard import keyboard


locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()


def italarm_signal_handler(signal, stack):
    player.show_track()


def interrupt_signal_handler(signal, frame):
    print 'Exitting...\n'
    GPIO.cleanup()
    sys.exit()


def usr1_signal_handler(signal, stack):
    pass


def pwrdn():
    subprocess.call(['sudo', 'shutdown', '-h', 'now'])


class ttree:

    def __init__(self, start_dir):
        self.tree = dict()
        self.home_dir = start_dir
        self.curr_dir = start_dir

        for root, dirs, files in os.walk(self.home_dir, followlinks=True):
            directory_has_music = False
            music_files = []
            files.sort()
            for filename in files:
                if filename.endswith(('.ogg', '.mp3', '.wav',
                                      '.flac', '.m4a', '.wma')):
                    music_files.append(filename)
                    directory_has_music = True
            if directory_has_music:
                self.tree[root] = music_files

    def list_dir(self):
        self.subdirectories_with_music = []
        for subdir in sorted(self.tree.keys()):
            if subdir.startswith(self.curr_dir) and \
                    len(subdir.split('/')) > len(self.curr_dir.split('/')):
                self.subdirectories_with_music.append(
                    subdir.split('/')[len(self.curr_dir.split('/'))]
                    )
        self.subdirectories_with_music.append('..')
        self.subdirectories_with_music = sorted(list(set(
            self.subdirectories_with_music
            )))

    def goto_dir(self, num, change_directory=True):
        if self.subdirectories_with_music[num] != '..':
            try_dir = os.path.join(
                self.curr_dir, self.subdirectories_with_music[num])
        else:
            if len(self.curr_dir) > len(self.home_dir):
                try_dir = self.curr_dir[:-len(self.curr_dir.split('/')[-1])-1]
            else:
                try_dir = self.curr_dir
        if change_directory:
            self.curr_dir = try_dir
        else:
            return try_dir

    def not_root_dir_chosen(self, offs):
        if self.subdirectories_with_music[offs] != '..':
            return True
        else:
            return False


class tplayer:

    def __init__(self, start_dir):
        self.playmode = False
        # subprocess.check_output(['mpc', 'update'])
        self.dirs = ttree(start_dir)
        self.dirs.list_dir()
        self.offs = 0

    def enter_dir(self):
        self.dirs.goto_dir(self.offs)
        self.dirs.list_dir()
        self.offs = 0

    def play(self):
        subprocess.call(['mpc', 'clear'])
        subprocess.call([
            'mpc', 'add',
            self.dirs.goto_dir(self.offs, False)[len(self.dirs.home_dir)+1:]
            ])
        subprocess.call(['mpc', 'play'])
        self.playmode = True
        place_text(self.dirs.subdirectories_with_music[self.offs], 0)
        self.show_track()
        signal.setitimer(signal.ITIMER_REAL, 5, 5)

    def stop(self):
        self.playmode = False
        signal.setitimer(signal.ITIMER_REAL, 0, 0)
        subprocess.call(['mpc', 'stop'])

    def prev(self):
        subprocess.call(['mpc', 'prev'])
        self.show_track()

    def next(self):
        subprocess.call(['mpc', 'next'])
        self.show_track()

    def inc_vol(self):
        subprocess.call(['amixer', '-c', '0', 'set', 'PCM', '1%+'])

    def dec_vol(self):
        subprocess.call(['amixer', '-c', '0', 'set', 'PCM', '1%-'])

    def seek(self, secs):
        subprocess.call(['mpc', 'seek', secs])

    def pause(self):
        subprocess.call(['mpc', 'toggle'])

    def show_track(self):
        sout = subprocess.check_output(['mpc', 'status']).splitlines()[0]
        print sout
        sout = sout.split('-')[-1]
        sout = sout.split('/')[-1]
        if sout[0] == ' ':
            sout = sout[1:]
        place_text(sout, 1)


def display(strings, offset=0):
    if not player.playmode:
        for i, item in enumerate(strings[offset:]):
            text = item.decode('utf-8', 'ignore')[:15]\
                    .encode('utf-8', 'ignore')
            if i == 0:
                place_text('>'+text, 0)
            if i == 1:
                place_text('\n'+text, 1)

    else:
        place_text(strings[0], 0)
        place_text(strings[1], 1)


def place_text(strings, row):
    s = strings+' '*(16-len(strings))
    if row == 1:
        s = '\n' + s
    lcd.message(s)

#####################################

lcd = HD44780()
buttons = keyboard()

place_text('Player v 1.0', 0)
place_text('-= loading =-', 1)


player = tplayer('/mnt/hd1/pi/Music')

signal.signal(signal.SIGALRM, italarm_signal_handler)
signal.signal(signal.SIGINT, interrupt_signal_handler)
signal.signal(signal.SIGUSR1, usr1_signal_handler)


#####################################

while 1:

    if not player.playmode:
        display(player.dirs.subdirectories_with_music, player.offs)
    signal.pause()
    while len(buttons.queue) > 1:
        k = buttons.queue.pop()
        if not player.playmode:  # choosemode
            if k == 'enter':
                player.enter_dir()
            if k == 'eject':
                player.offs = 0
                player.enter_dir()
            if k == 'play' and player.dirs.not_root_dir_chosen(player.offs):
                player.play()
            if k == 'back' and player.offs > 0:
                player.offs -= 1
            if k == 'fwd' and player.offs < \
                    len(player.dirs.subdirectories_with_music)-1:
                player.offs += 1
        else:  # playmode
            if k == 'eject':
                player.stop()
            if k == 'back':
                player.prev()
            if k == 'fwd':
                player.next()
            if k == 'vol+':
                player.inc_vol()
            if k == 'vol-':
                player.dec_vol()

            if k == 'play':
                player.pause()
        if k == 'pwr':
            place_text('Player v 1.0', 0)
            place_text('-= shutdown =-', 1)
            GPIO.cleanup()
            pwrdn()
