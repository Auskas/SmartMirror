#! python3
# youtube_widget.py

import logging
from tkinter import *
import vlc
vlc.logger.setLevel(logging.CRITICAL)
import sys
import logging
import time
import threading
import urllib.request
import urllib.parse
import re
import time
import alsaaudio

class Youtuber:

    def __init__(self, window, gesturesAssistant, voiceAssistant, waveWidget):
        self.logger = logging.getLogger('Gesell.youtuber.Youtuber')
        self.window = window
        self.gesturesAssistant = gesturesAssistant
        self.waveWidget = waveWidget
        # self.w and self.h are the dimension of the main window. They are used to switch the video into fullscreen mode.
        self.w, self.h = self.window.winfo_screenwidth(), self.window.winfo_screenheight()
        self.voiceAssistant = voiceAssistant
        _isMacOS   = sys.platform.startswith('darwin')
        _isWindows = sys.platform.startswith('win')
        _isLinux = sys.platform.startswith('linux')
        args = ['--no-ts-trust-pcr', '--ts-seek-percent', '--video-wallpaper', '--ts-seek-percent',
                '--play-and-exit', '--verbose=0', '--vout=X11'] #,, '--aout=alsa']
        if _isLinux:
            args.append('--no-xlib')
            
        # Below are some Youtube links for testing purposes. Leave one uncommented to see it on the screen.
        #self.url = str('https://www.youtube.com/watch?v=9Auq9mYxFEE') # Sky News
        #self.url = str('https://www.youtube.com/watch?v=P-_lx0ysHfw') # Spartak
        self.url = str('https://www.youtube.com/watch?v=diRtRhcaUNI') # Metallica
        #self.url = str('https://www.youtube.com/watch?v=BkNqOnIEOyc') # Rock/metal live radio
        #self.url = str ('https://www.youtube.com/watch?v=RjIjKNcr_fk') # Al Jazeera
        
        self.instance = vlc.Instance(args)

        # Creating the media object (Youtube video URL).
        self.media = self.instance.media_new(self.url)
        self.media_list = self.instance.media_list_new([self.url]) # Creating a list of one video from Youtube

        # Creating an instance of the player.
        self.player = self.instance.media_player_new()
        self.player.set_media(self.media)
        self.player.audio_set_volume(100)

        # Creating a new MediaListPlayer instance and associating the player and playlist with it.
        self.list_player = self.instance.media_list_player_new()
        self.list_player.set_media_player(self.player)
        self.list_player.set_media_list(self.media_list)

        # Videos are played in the canvas, which size can be adjusted in order to show it fullscreen.
        self.widgetCanvas = Canvas(self.window, width=self.w * 0.3, height=self.w * 0.3 * 0.5625, 
                                            bg='black', borderwidth=0, highlightbackground='black')
        self.widgetCanvas.place(relx=0.97, rely=0.8, anchor='se')

        # Set the window id where to render VLC's video output.
        h = self.widgetCanvas.winfo_id()
        self.player.set_xwindow(h)
        self.player.set_fullscreen(False)
        self.set_window()
        self.fullscreen_status = False
        self.audio = alsaaudio.Mixer()
        self.player.play()
        self.logger.info('Youtube widget has been initialized.')
        #self.status()

    def status(self):
        """ The method is used to follow the Voice assistant cmd set.
        When the user gives a command or commands connected to the video widget,
        the set will contain those commands."""
        while True:
            if self.gesturesAssistant.command == 'VoiceControl':
                volume = self.player.audio_get_volume()
                if volume > 0:
                    self.player.audio_set_volume(0)
                    self.waveWidget.change_status()
                    time.sleep(2)
                    voiceThread = threading.Thread(target=self.voiceAssistant.myCommand)
                    voiceThread.start()
                    voiceThread.join()
                    print(self.voiceAssistant.cmd)
                    if len(self.voiceAssistant.cmd) > 0:
                        for c in self.assistant.cmd:
                            if c == 'fullscreen':
                                print('FULLSCREEN!')
                                self.set_fullscreen()
                            elif c == 'window':
                                print('WINDOW!!!')
                                self.set_window()
                            elif c.find('play') != -1:
                                topic = c.replace('play ', '')
                                print(topic)
                                #searchThread = threading.Thread(target=self.search, args=(topic,))
                                #searchThread.start()
                                self.search(topic)
                    self.waveWidget.change_status()
                    self.player.audio_set_volume(volume)
                    self.voiceAssistant.cmd = set()
            #print('Waiting for command...')
            time.sleep(0.05)

    def search(self, topic):
        """ The method is used to get Youtube link of the desired topic.
        It loads the webpage using a proper request and find the URL of the most relevant video.
        At the end it calls change_url method to actually change the URL of video.
        Arguments: topic as a string."""
        query_string = urllib.parse.urlencode({"search_query" : topic})
        html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
        search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
        #print(search_results[0])
        self.change_url("https://www.youtube.com/watch?v=" + search_results[0])

    def change_url(self, url):
        """ The method is used to change video's URL.
        It stops the player, creates a media object with the requested source,
        creates a list of media containing only one media and
        associates the list to the player. Afterwards the player restarts.
        Arguments: url as a string."""
        self.player.stop()
        self.media = self.instance.media_new(url)
        self.media_list = self.instance.media_list_new([url])
        self.player.set_media(self.media)
        self.list_player = self.instance.media_list_player_new()
        self.list_player.set_media_player(self.player)
        self.list_player.set_media_list(self.media_list)
        print('Changing the URL for video player...')
        self.player.play()

    def set_window(self):
        """ The method is used to change the size of the video canvas.
        The canvas occupies only small part of the main window."""
        self.widgetCanvas.place(relx=0.97, rely=0.8, anchor='se')
        self.widgetCanvas.config(width=self.w * 0.3, height=self.h * 0.3 * 0.5625)
        self.fullscreen_status = False

    def set_fullscreen(self):
        """ The method is used to change the size of the video canvas
        The canvas size equals to the size of the screen.
        Therefore it occupies fullscreen."""
        self.widgetCanvas.place(relx=0, rely=0, anchor='nw')
        self.widgetCanvas.config(width=self.w, height=self.h)
        self.fullscreen_status = True

class Assistant:

    def __init__(self):
        self.cmd = ['play manowar warrior of the world']

class GesturesAssistant:

    def __init__(self):
        self.command = 'VoiceControl'

if __name__ == '__main__':
    try:
        window = Tk()
        window.title('Main Window')
        window.configure(bg='black')
        #window.overrideredirect(True)
        w, h = window.winfo_screenwidth(), window.winfo_screenheight()
        window.geometry("%dx%d+0+0" % (w, h))
        #assistant = Assistant()
        gesturesAssistant = GesturesAssistant()
        youtuber = Youtuber(window, gesturesAssistant)
        window.mainloop()
    except KeyboardInterrupt:
        sys.exit()
