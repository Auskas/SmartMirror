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

class Youtuber:

    def __init__(self, window):
        self.window = window
        # self.w and self.h are the dimension of the main window. They are used to switch the video into fullscreen mode.
        self.w, self.h = self.window.winfo_screenwidth(), self.window.winfo_screenheight()
        #self.assistant = assistant
        _isMacOS   = sys.platform.startswith('darwin')
        _isWindows = sys.platform.startswith('win')
        _isLinux = sys.platform.startswith('linux')
        args = ['--ts-seek-percent', '--video-wallpaper', '--ts-seek-percent',
                '--play-and-exit', '--verbose=0', '--vout=X11'] #,'--no-ts-trust-pcr', '--aout=alsa']
        if _isLinux:
            args.append('--no-xlib')
            
        # Below are some Youtube links for testing purposes. Leave one uncommented to see it on the screen.
        #self.url = str('https://www.youtube.com/watch?v=9Auq9mYxFEE') # Sky News
        #self.url = str('https://www.youtube.com/watch?v=P-_lx0ysHfw') # Spartak
        #self.url = str('https://www.youtube.com/watch?v=diRtRhcaUNI') # Metallica
        #self.url = str('https://www.youtube.com/watch?v=BkNqOnIEOyc') # Rock/metal live radio
        self.url = str ('https://www.youtube.com/watch?v=RjIjKNcr_fk') # Al Jazeera
        
        self.instance = vlc.Instance(args)

        # Creating the media object (Youtube video URL).
        self.media = self.instance.media_new(self.url)
        self.media_list = self.instance.media_list_new([self.url]) # Creating a list of one video from Youtube

        # Creating an instance of the player.
        self.player = self.instance.media_player_new()
        self.player.set_media(self.media)

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
        #self.player.play()
        #except Exception as error:
           # print(error)
        # Plays video in fullscreen.   
        #self.set_fullscreen()
        #self.status()

    def status(self):
        """ The method is used to follow the Voice assistant cmd set.
        When the user gives a command or commands connected to the video widget,
        the set will contain those commands."""
        self.player.play()
        #print(self.player.audio_get_channel())
        #self.player.audio_get_channel()
        """for c in self.assistant.cmd:
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
                self.search(topic)"""
        #self.assistant.cmd = set()
        self.widgetCanvas.after(2000, self.status)

    def search(self, topic):
        """ The method is used to get Youtube link of the desired topic.
        It loads the webpage using a proper request and find the URL of the most relevant video.
        At the end it calls change_url method to actually change the URL of video.
        Arguments: topic as a string."""
        #command=['youtube-dl', f'ytsearch:"{topic}"', '-e']
        #result=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True).stdout.split()
        #print(result)
        #if len(result) > 0:
            #self.change_url(result[0])
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
        self.widgetCanvas.config(width=self.w * 0.4, height=self.h * 0.225)

    def set_fullscreen(self):
        """ The method is used to change the size of the video canvas
        The canvas size equals to the size of the screen.
        Therefore it occupies fullscreen."""
        self.widgetCanvas.place(relx=0, rely=0, anchor='nw')
        self.widgetCanvas.config(width=self.w, height=self.h)

class Assistant:

    def __init__(self):
        self.cmd = ['play manowar warrior of the world']

if __name__ == '__main__':
    try:
        window = Tk()
        window.title('Main Window')
        window.configure(bg='black')
        window.overrideredirect(True)
        w, h = window.winfo_screenwidth(), window.winfo_screenheight()
        window.geometry("%dx%d+0+0" % (w, h))
        #assistant = Assistant()
        youtuber = Youtuber(window)
        window.mainloop()
    except KeyboardInterrupt:
        sys.exit()
