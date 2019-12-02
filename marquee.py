#! python3
# marquee.py - a marquee for my Smart Mirror Project.

from tkinter import *
import datetime
import time
import logging

class Marquee(Canvas):

    def __init__(self, frame, newsrubot, fps=120):
        self.logger = logging.getLogger('Gesell.marquee.Marquee')
        self.logger.debug('Initializing an instance of Marquee Widget...')
        self.newsruBot = newsrubot
        # borderwidth default size is 2 (we don't need any borders), highlightbackground default is white - when the canvas is not in the focus.
        Canvas.__init__(self, frame,  bg='black', borderwidth=0, highlightbackground='black')
        self.fps = fps
        text = ''.join(self.newsruBot.news) + '\n'
        self.text_id = self.create_text(0, 0, text=text, anchor="w", fill='lightblue', font=("SF UI Display Semibold", 21, "bold"), tags=("text",))
        (x0, y0, x1, y1) = self.bbox("text")
        x1 = frame.winfo_screenwidth() - int(0.06 * (frame.winfo_screenwidth()))
        width = (x1 - x0)
        height = (y1 - y0)
        self.configure(width=width, height=height)
        self.place(relx=0.03, rely=0.84)
        self.logger.debug('An instance of Marquee Widget has been created.')
        self.animate()

    def animate(self):
        (x0, y0, x1, y1) = self.bbox("text")
        if x1 < 0 or y0 < 0:
            # The text is off the screen. Resetting the x while also getting the news from newsruBot.
            text = ''.join(self.newsruBot.news) + '\n'
            self.itemconfig(self.text_id, text=text)
            #print('Gotcha!', x0,y0,x1,y1)
            x0 = self.winfo_width()
            y0 = int(self.winfo_height()/2)
            #print(x0,y0,x1,y1)
            self.coords("text", x0, y0)
        else:
            self.move("text", -1, 0)
        self.after_id = self.after(int(1000/self.fps), self.animate)
