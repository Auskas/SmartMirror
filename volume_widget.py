#!/usr/bin/python3
# volume_widget.py - a volume control widget that resemble the iOS volume control.

from tkinter import *
import logging
import os
from PIL import Image, ImageTk
import cv2

class Volume:

    def __init__(self, frame):
        self.logger = logging.getLogger('Gesell.volume_widget.Volume')
        self.logger.debug('Initializing an instance of Volume Widget...')
        self.frame = frame

        self.w, self.h = self.frame.winfo_screenwidth(), self.frame.winfo_screenheight()

        # Target size of the icons is a tuple. The height and width are one fiftieth of the screen height.
        self.icons_target_size = (int(self.w // 50), int(self.w // 50))
        self.volume_frame_width = int(self.w * 0.3)
        self.volume_frame_height = self.icons_target_size[0]
        # The range in pixels of the space between the muted speaker icon and the loud speaker to the right.
        self.volume_range = int(self.volume_frame_width - 3 * self.volume_frame_height)

        #self.volume_frame = Frame(frame, bg='black', bd=0)
        #self.volume_frame.place(   relx=0.67, rely=0.63 - int(self.icons_target_size[0] / self.h)   )

        self.volume_frame = Canvas(self.frame, width=self.volume_frame_width,
                                   height=self.volume_frame_height, bg='black',
                                   borderwidth=0, highlightbackground='black')

        self.volume_frame.place(
            relx=0.97, 
            rely=0.8 - (self.volume_frame_width * 0.5625) / self.h - self.icons_target_size[0] / self.h, 
            anchor='se'
            )

        # Loads the images, that are used in the widget, resizes them and assigns to the widget.
        image_bar = Image.open(f'icons{os.sep}volume_bar.png')
        image_bar = image_bar.resize((self.volume_range + self.volume_frame_height, self.icons_target_size[0]), Image.ANTIALIAS)
        render_bar = ImageTk.PhotoImage(image_bar)

        image_speaker = Image.open(f'icons{os.sep}speaker.png')
        image_speaker = image_speaker.resize(self.icons_target_size, Image.ANTIALIAS)
        render_speaker = ImageTk.PhotoImage(image_speaker)

        image_speaker_loud = Image.open(f'icons{os.sep}speaker_loud.png')
        image_speaker_loud = image_speaker_loud.resize(self.icons_target_size, Image.ANTIALIAS)
        render_speaker_loud = ImageTk.PhotoImage(image_speaker_loud)

        image_speaker_ball = Image.open(f'icons{os.sep}speaker_ball.png')
        image_speaker_ball = image_speaker_ball.resize(self.icons_target_size, Image.ANTIALIAS)
        render_speaker_ball = ImageTk.PhotoImage(image_speaker_ball)

        self.icon_speaker = Label(self.volume_frame, image=render_speaker, bg='black')
        self.icon_speaker.image = render_speaker
        
        #self.speaker_ball_position_absolute = round((self.youtuber.audio_volume * self.volume_range) / 100) + self.volume_frame_height

        self.icon_bar = Label(self.volume_frame, image=render_bar, bg='black')
        self.icon_bar.image = render_bar
        
        self.icon_speaker_ball = Label(self.volume_frame, image=render_speaker_ball, bg='black')
        self.icon_speaker.ball = render_speaker_ball

        self.icon_speaker_loud = Label(self.volume_frame, image=render_speaker_loud, bg='black')
        self.icon_speaker_loud.image = render_speaker_loud

        self.is_concealed = False
        self.hide()
        
    
    def show(self):
        self.volume_frame.config(width=self.volume_frame_width, 
                                 height=self.volume_frame_height)
        self.is_concealed = False

    def hide(self):
        self.volume_frame.config(width=0, height=0)
        self.is_concealed = True

    def ball_position(self, volume):
        self.icon_speaker.place(relx=0, rely=0, anchor='nw')
        self.icon_bar.place(x=self.volume_frame_height, rely=0, anchor='nw')

        self.speaker_ball_position_absolute = round((volume * self.volume_range) / 100) + self.volume_frame_height
        self.icon_speaker_ball.place(x=self.speaker_ball_position_absolute, rely=0, anchor='nw')

        self.icon_speaker_loud.place(relx=1, rely=0, anchor='ne')




if __name__ == '__main__':
    class Youtuber:
        def __init__(self):
            self.audio_volume = 60
    youtuber = Youtuber()
    window = Tk()
    window.title('Main Window')
    window.configure(bg='black')
    #window.overrideredirect(True)
    w, h = window.winfo_screenwidth(), window.winfo_screenheight()
    window.geometry("%dx%d+0+0" % (w, h))
    a = Volume(window, youtuber)
    window.mainloop()
        


        

