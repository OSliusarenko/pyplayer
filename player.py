#!/usr/bin/python

""" Main script"""

import os
import signal
import locale
import subprocess
import RPi.GPIO as GPIO
from mpd import MPDClient
import sys
from HD44780 import HD44780
from keyboard import Keyboard


locale.setlocale(locale.LC_ALL, '')
# code = locale.getpreferredencoding()
VERSION = '1.1'


def italarm_signal_handler(ssignal, stack):
    """ Shows the current playing track """
    PLAYER.show_track()


def interrupt_signal_handler(ssignal, frame):
    """ Cleans out pins when ^C received"""
    print 'Exitting...\n'
    PLAYER.exit()
    GPIO.cleanup()
    sys.exit()


def usr1_signal_handler(ssignal, stack):
    """ Temporarily nothing """
    pass


def pwrdn():
    """ Shuts down the device when pwdn pressed """
    subprocess.call(['sudo', 'shutdown', '-h', 'now'])


class Tree(object):
    """ Directories with music files """

    def __init__(self, start_dir):
        """ Mainly finds files suitable for playing """
        self.tree = dict()
        self.home_dir = start_dir
        self.curr_dir = start_dir
        self.subdirectories_with_music = []

        for root, _, files in os.walk(self.home_dir, followlinks=True):
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
        """ Collects DB of directories with music files """
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
        """ Navigates to the specified directory """
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
        """ Checks whether play pressed not in for root dir """
        if self.subdirectories_with_music[offs] != '..':
            return True
        else:
            return False


class Player(object):
    """ Main class """

    def __init__(self, start_dir):
        """ Init player """
        self.playmode = False
        self.mpc = MPDClient(use_unicode=True)
        self.mpc.connect("localhost", 6600)
        self.mpc.update()
        self.dirs = Tree(start_dir)
        self.dirs.list_dir()
        self.offs = 0

    def enter_dir(self):
        """ Goto specified directory """
        self.dirs.goto_dir(self.offs)
        self.dirs.list_dir()
        self.offs = 0

    def play(self):
        """ Play the files """
        try:
            self.mpc.clear()
            self.mpc.add(
                self.dirs.goto_dir(self.offs, False)[len(self.dirs.home_dir)+1:]
                )
            self.mpc.play()
            self.playmode = True
            place_text(self.dirs.subdirectories_with_music[self.offs], 0)
            self.show_track()
            signal.setitimer(signal.ITIMER_REAL, 5, 5)
        except:
            pass

    def stop(self):
        """ Stop playing """
        self.playmode = False
        signal.setitimer(signal.ITIMER_REAL, 0, 0)
        self.mpc.stop()

    def prev(self):
        """ Previous track """
        self.mpc.previous()
        self.show_track()

    def next(self):
        """ Next track """
        self.mpc.next()
        self.show_track()
        
    def exit(self):
        """ Exit mpd client """
        self.mpc.close()
        self.mpc.disconnect()

    @staticmethod
    def inc_vol():
        """ Increase volume """
        subprocess.call(['amixer', '-c', '1', 'set', 'PCM', '1%+'])

    @staticmethod
    def dec_vol():
        """ Decrease volume """
        subprocess.call(['amixer', '-c', '1', 'set', 'PCM', '1%-'])

    def seek(self, secs):
        """ Seek file """
        self.mpc.seekcur(secs)

    def pause(self):
        """ Toggle state: play/pause """
        self.mpc.pause()

    def show_track(self):
        """ Show playing track on LCD """
        s = self.mpc.currentsong()
        if s != {}:
            place_text(s['artist'], 0)
            place_text(s['title'], 1)
        else:
            place_text(' '*16, 0)
            place_text('   -= END =-   ', 1)


def display(strings, offset=0):
    """ Display info on LCD regarding playmode """
    if not PLAYER.playmode:
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
    """ Wrapper for LCD """
    s_tmp = strings+' '*(16-len(strings))
    if row == 1:
        s_tmp = '\n' + s_tmp
    LCD.message(s_tmp)

#####################################

LCD = HD44780()
BUTTONS = Keyboard()

place_text('Player v' + VERSION, 0)
place_text('-= loading =-', 1)


PLAYER = Player('/home/pi/Music')

signal.signal(signal.SIGALRM, italarm_signal_handler)
signal.signal(signal.SIGINT, interrupt_signal_handler)
signal.signal(signal.SIGUSR1, usr1_signal_handler)


#####################################

while 1:

    if not PLAYER.playmode:
        display(PLAYER.dirs.subdirectories_with_music, PLAYER.offs)
    signal.pause()
    while len(BUTTONS.queue) > 1:
        k = BUTTONS.queue.pop()
        if not PLAYER.playmode:  # choosemode
            if k == 'enter':
                PLAYER.enter_dir()
            if k == 'eject':
                PLAYER.offs = 0
                PLAYER.enter_dir()
            if k == 'play' and PLAYER.dirs.not_root_dir_chosen(PLAYER.offs):
                PLAYER.play()
            if k == 'back' and PLAYER.offs > 0:
                PLAYER.offs -= 1
            if k == 'fwd' and PLAYER.offs < \
                    len(PLAYER.dirs.subdirectories_with_music)-1:
                PLAYER.offs += 1
        else:  # playmode
            if k == 'eject':
                PLAYER.stop()
            if k == 'back':
                PLAYER.prev()
            if k == 'fwd':
                PLAYER.next()
            if k == 'vol+':
                PLAYER.inc_vol()
            if k == 'vol-':
                PLAYER.dec_vol()

            if k == 'play':
                PLAYER.pause()
        if k == 'pwr':
            place_text('Player v' + VERSION, 0)
            place_text('-= shutdown =-', 1)
            PLAYER.exit()
            GPIO.cleanup()
            pwrdn()
