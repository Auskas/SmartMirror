#!/usr/bin/python3
# youtube_lua.py
# The script downloads 'youtube.lua' file that is used for playing Youtube videos through VLC player.
# It also overwrites the existing file with the freshly downloaded one.
# Please check the __init__ method of the LuaUpdater class to make sure that target file path is relevant to your system.
# As default, the target file path is associated with Raspbian.

import os, sys
import time
import requests
import logging
import subprocess

class LuaUpdater:

    def __init__(self):
        # The module is part of my SmartMirror project, therefore the following logging convention is used.
        self.logger = logging.getLogger('Gesell.youtube_lua.LuaUpdater')

        if __name__ == '__main__': # Creates a logger if the module is called directly.
            ch = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.setLevel(logging.DEBUG)
            self.logger.addHandler(ch)

        if os.geteuid() == 0:
            self.logger.debug('Script is running under root privileges.')
            self.is_root = True
        else:
            self.logger.debug('Script is not running under root privileges.')
            self.is_root = False
        # The source URL where the lua file is located. The community periodically updates the file responding to
        # changes in Youtube algorithms.
        self.url = 'https://raw.githubusercontent.com/videolan/vlc/master/share/lua/playlist/youtube.lua'
        # The target file path is relevant to Raspbian OS. Make your changes accordingly to your OS.
        self.target_file = '/usr/lib/arm-linux-gnueabihf/vlc/lua/playlist/youtube.luac'
        # The path to a temp file prior to copying it to the destination (OS dependant).
        self.temp_file = '/home/pi/SmartMirror/Lua/youtube.lua'
        self.update_rate = 86400 # time in seconds till next update.

    def get_page(self, link):
        """ Loads a web page using 'requests' module. Returns the result as text if the status is OK.
        Otherwise, returns False."""
        try:
            res = requests.get(link)
        except Exception as error:
            self.logger.error(f'Cannot load the page, the following error occured: {error}')
            return False
        try:
            res.raise_for_status()
            self.logger.debug('Page {0} has been successfully loaded.'.format(link))
            return res.text
        except Exception as error:
            self.logger.error('Cannot get the page {0}'.format(link))
            self.logger.error('The following error occured: {0}'.format(error))
            return False

    def updater(self):
        """ Periodically downloads the lua file. The method does not check the version of the file.
            If the module is executed under root privileges, the newly obtained data is written directly to the destination file.
            Otherwise, a subprocess is called to copy the file."""
        luac = self.get_page(self.url)
        if luac:
            if self.is_root:
                with open(self.target_file, 'w') as target_file:
                    target_file.write(luac)
                self.logger.debug('youtube.luac has been successfully updated.')
            else:
                with open(self.temp_file, 'w') as temp_file:
                    temp_file.write(luac)
                self.logger.debug('youtube.luac has been saved to a temp file.')
                try:
                    subprocess.call(['sudo', 'cp', '-rf', self.temp_file, self.target_file])
                    self.logger.debug('youtube.luac has been successfully updated.')
                except Exception as error:
                    self.logger.debug(f'Cannot rewrite the file: {error}')
        time.sleep(self.update_rate)

if __name__ == '__main__':
    updater = LuaUpdater()
    updater.updater()
