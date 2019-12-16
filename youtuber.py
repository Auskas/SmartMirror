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
from random import choice

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
        args = ['--video-wallpaper', '--play-and-exit', '--verbose=0', '--aout=alsa',
                '--vout=X11', '--network-caching=1000'] 
               #'--no-ts-trust-pcr', '--ts-seek-percent',  '--file-logging', '--logfile=vlc-log.txt', '--aout=alsa'
        if _isLinux:
            args.append('--no-xlib')
        # Below are some Youtube links for testing purposes. Leave one uncommented to see it on the screen.
        #self.url = str('https://www.youtube.com/watch?v=9Auq9mYxFEE') # Sky News
        self.url = str('https://www.youtube.com/watch?v=fdN46JyP1lI') # Football Club 1
        #self.url = str('https://www.youtube.com/watch?v=-fLF_ejuOjs&pbjreload=10') # Football Club 2
        #self.url = str('https://www.youtube.com/watch?v=P-_lx0ysHfw') # Spartak
        #self.url = str('https://www.youtube.com/watch?v=diRtRhcaUNI') # Metallica
        #self.url = str('https://www.youtube.com/watch?v=n_GFN3a0yj0') # AC/DC Thunderstruck
        #self.url = str('https://www.youtube.com/watch?v=BkNqOnIEOyc') # Rock/metal live radio
        #self.url = str('https://www.youtube.com/watch?v=RjIjKNcr_fk') # Al Jazeera
        #self.url = str('https://www.youtube.com/watch?v=wqPby9nOAKI') # NTV Russia live
        #self.url = str('https://www.youtube.com/watch?v=qFs5CtoEfDo') # Редакция
        
        self.instance = vlc.Instance(args)
        
        # Creating the media object (Youtube video URL).
        #self.media = self.instance.media_new(self.url)
        
        # Creating an instance of MediaList object and assigning it a tuple containing only one URL from Youtube.
        self.media_list = self.instance.media_list_new((self.url, ))

        # Creating an instance of the player.
        self.player = self.instance.media_player_new()
        self.player.audio_set_volume(100)
        
        # Creating a new MediaListPlayer instance and associating the player and playlist with it.
        self.list_player = self.instance.media_list_player_new()
        self.list_player.set_media_player(self.player)
        self.list_player.set_media_list(self.media_list)
        
        # Videos are played in the canvas, which size can be adjusted in order to show it fullscreen.
        self.video_window_width = int(self.w * 0.3)
        self.video_window_height = int(self.video_window_width * self.h / self.w)
        self.widgetCanvas = Canvas(self.window, width=self.video_window_width,
                                   height=self.video_window_height, bg='black',
                                   borderwidth=0, highlightbackground='black')
        self.widgetCanvas.place(relx=0.97, rely=0.8, anchor='se')
        # Set the window id where to render VLC's video output.
        self.widget_canvas_id = self.widgetCanvas.winfo_id()
        self.player.set_xwindow(self.widget_canvas_id)
        self.player.set_fullscreen(False)
        #self.set_window()
        self.fullscreen_status = False
        self.audio = alsaaudio.Mixer()
        self.list_player.play()
        self.video_status = 'running'
        #self.player.play()
        self.logger.info('Youtube widget has been initialized.')

    def status(self):
        """ The method is used to follow the Voice assistant cmd set.
        When the user gives a command or commands connected to the video widget,
        the set will contain those commands."""
        while True:
            if self.gesturesAssistant.command == 'VoiceControl':
                self.logger.debug('Voice control gesture detected!')
                volume = self.player.audio_get_volume()
                if volume > 0:
                    self.player.audio_set_volume(0)
                time.sleep(0.5)
                siriChimeThread = threading.Thread(target=self.waveWidget.play)
                siriChimeThread.start()
                self.waveWidget.play()
                self.waveWidget.change_status()
                self.voiceAssistant.myCommand()
                #voiceThread = threading.Thread(target=self.voiceAssistant.myCommand)
                #voiceThread.start()
                #voiceThread.join()
                if len(self.voiceAssistant.cmd['youtube']) > 0:
                    print('Processing voice command...')
                    for c in self.voiceAssistant.cmd['youtube']:
                        if c == 'fullscreen':
                            self.logger.debug('Switching to video fullscreen mode...')
                            self.set_fullscreen()
                        elif c == 'window':
                            self.logger.debug('Switching to video window mode...')
                            self.set_window()
                        elif c.find('playback stop') != -1:
                            self.set_window()
                            self.video_stop()
                        elif c.find('playback pause') != -1:
                            self.list_player.pause()
                        elif c.find('playback resume') != -1:
                            self.video_status()
                            self.list_player.play()
                        elif c.find('video search') != -1:
                            self.video_status()
                            topic = c.replace('video search ', '')
                            #searchThread = threading.Thread(target=self.search, args=(topic,))
                            #searchThread.start()
                            self.logger.debug(f'Processing video request {topic}.')
                            self.search(topic)
                self.waveWidget.change_status()
                #print(self.media_list.count(), self.player.get_instance())
                self.player.audio_set_volume(volume)
                self.voiceAssistant.cmd['youtube'] = set()
                self.gesturesAssistant.command = 'None'
            #print('Waiting for command...')
            #print(volume, self.player.audio_get_volume()) 
            time.sleep(0.05)
            
    def video_status(self):
        if self.fullscreen_status:
            self.widgetCanvas.place(relx=0, rely=0, anchor='nw')
            self.widgetCanvas.config(width=self.w, height=self.h)
        else:
            self.widgetCanvas.place(relx=0.97, rely=0.8, anchor='se')
            self.widgetCanvas.config(width=self.video_window_width, height=self.video_window_height)
            
    def video_stop(self):
        self.widgetCanvas.config(width=0, height=0)
        self.list_player.pause()
        self.video_status = 'stopped'
     
    def search(self, topic):
        """ The method is used to get Youtube link of the desired topic.
        It loads the webpage using a proper request and find the URL of the most relevant video.
        At the end it calls change_url method to actually change the URL of video.
        Arguments: topic as a string."""
        
        self.logger.debug(f'Youtube URL searching for {topic}...')
        query_string = urllib.parse.urlencode({"search_query" : topic})
        
        try:
            html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
            search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
            
        except Exception as error:
            self.logger.debug(f'Cannot load Youtube: {error}')
            
        self.logger.debug('Found the URL for the requested video...')
        self.change_url("https://www.youtube.com/watch?v=" + search_results[0])
        
    def change_url(self, url):
        """ The method is used to change video's URL.
        It stops the player, creates a media object with the requested source,
        creates a list of media containing only one media and
        associates the list to the player. Afterwards the player restarts.
        Arguments: url as a string."""
        self.logger.debug(f'Changing URL of the media player: {url}')
        # In order to change the video, the script pauses the player, removes first (and only) video
        # in the media list, adds target URL to the media list, virtually presses next video in
        # the player and finally resumes the playback.
        self.list_player.pause()
        
        self.media_list.remove_index(0)        
        self.media_list.add_media(url)        
        self.list_player.next()

        self.player.set_xwindow(self.widget_canvas_id)        

        self.list_player.play()
        
        self.video_status = 'running'
        
        self.logger.debug('The URL has been changed.')

    def set_window(self):
        """ The method is used to change the size of the video canvas.
        The canvas occupies only small part of the main window."""
        self.widgetCanvas.place(relx=0.97, rely=0.8, anchor='se')
        self.widgetCanvas.config(width=self.video_window_width, height=self.video_window_height)
        self.player.set_xwindow(self.widget_canvas_id)
        self.fullscreen_status = False
        self.video_status = 'running'

    def set_fullscreen(self):
        """ The method is used to change the size of the video canvas
        The canvas size equals to the size of the screen.
        Therefore it occupies fullscreen."""
        self.widgetCanvas.place(relx=0, rely=0, anchor='nw')
        self.widgetCanvas.config(width=self.w, height=self.h)
        self.player.set_xwindow(self.widget_canvas_id)
        self.fullscreen_status = True
        self.video_status = 'running'

class VoiceAssistant:

    def __init__(self):
        pass
        
    def myCommand(self):
        self.cmd = (choice(('play нтв программа чрезвычайное происшествие', 'play василий уткин футбольный клуб',
                            'play python asyncio', 'play iron maiden the trooper live', 'play guns n roses sweet child of mine'
                            'play world of tanks merceneries', 'play liverpool fc', 'play редакция')),)
        print(type(self.cmd))

class GesturesAssistant:

    def __init__(self):
        self.command = 'VoiceControl'
        #self.command = 'None'
        
class WaveWidget:
    def __init__(self):
        self.status = True
        
    def play(self):
        pass
    
    def change_status(self):
        if self.status:
            self.status = False
        else:
            self.status = True

if __name__ == '__main__':
    try:
        logging.basicConfig(level=logging.DEBUG)
        window = Tk()
        window.title('Main Window')
        window.configure(bg='black')
        #window.overrideredirect(True)
        w, h = window.winfo_screenwidth(), window.winfo_screenheight()
        window.geometry("%dx%d+0+0" % (w, h))
        voiceAssistant = VoiceAssistant()
        gesturesAssistant = GesturesAssistant()
        waveWidget = WaveWidget()
        youtuber = Youtuber(window, gesturesAssistant, voiceAssistant, waveWidget)
        youtuberThread = threading.Thread(target=youtuber.status)
        youtuberThread.daemon = True
        youtuberThread.start()
        window.mainloop()
    except KeyboardInterrupt:
        sys.exit()
