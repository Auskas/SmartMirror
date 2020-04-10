#!/usr/bin/python3
# covid.py - a widget that displays the current Covid-19 cases.

from tkinter import *
import logging
from PIL import Image, ImageTk
import os

class Covid:

    def __init__(self, frame, parserBot, gesturesAssistant):
        self.logger = logging.getLogger('Gesell.covid.Covid')
        if __name__ == '__main__': # Creates a logger if the module is called directly.
            ch = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.setLevel(logging.DEBUG)
            self.logger.addHandler(ch)
        self.logger.debug('Initializing an instance of Covid-19 Widget...')
        self.parserBot = parserBot
        self.gesturesAssistant = gesturesAssistant

        w, h = frame.winfo_screenwidth(), frame.winfo_screenheight()
        print(w,h)

        # Main frame for the widget.
        self.covid_frame = Frame(frame, bg='black', bd=0)
        self.covid_frame.place(relx=0.95, rely=0.15, anchor='ne')

        # The inner top frame with the world Covid-19 cases.
        self.top_frame = Frame(self.covid_frame, bg='black', bd=0)
        self.top_frame.grid(column=0, row=0, sticky='w')

        # The leftmost frame inside the top frame to display the total number of cases.
        self.top_frame_cases = Frame(self.top_frame, bg='black', bd=0)
        self.top_frame_cases.grid(column=0, row=0, sticky='w')

        # Loads and places the biohazard icon.
        icon_cases = Image.open(f'.{os.sep}icons{os.sep}biohazard.png')
        icon_cases = icon_cases.resize((int(w/50), int(w/50)), Image.ANTIALIAS)
        render_cases = ImageTk.PhotoImage(icon_cases)
        self.icon_cases_world = Label(self.top_frame_cases, image=render_cases, bg='black')
        self.icon_cases_world.image = render_cases
        self.icon_cases_world.grid(column=0, row=0, sticky='w')

        # The middle frame inside the top frame to display the number of deaths.
        self.world_cases = Label(self.top_frame_cases, text='0', fg='white', bg='black', font=("SFUIText", 14, "bold"))
        self.world_cases.grid(column=1, row=0, sticky='w')

        self.top_frame_deaths = Frame(self.top_frame, bg='black', bd=0)
        self.top_frame_deaths.grid(column=1, row=0, sticky='w')

        # Loads and places the scull icon.
        icon_deaths = Image.open(f'.{os.sep}icons{os.sep}dead.png')
        icon_deaths = icon_deaths.resize((int(w/50), int(w/50)), Image.ANTIALIAS)
        render_deaths = ImageTk.PhotoImage(icon_deaths)
        self.icon_deaths_world = Label(self.top_frame_deaths, image=render_deaths, bg='black')
        self.icon_deaths_world.image = render_deaths
        self.icon_deaths_world.grid(column=0, row=0, sticky='w')

        # The rightmost frame inside the top frame to display the number of recovered.
        self.world_deaths = Label(self.top_frame_deaths, text='0', fg='white', bg='black', font=("SFUIText", 14, "bold"))
        self.world_deaths.grid(column=1, row=0, sticky='w')

        self.top_frame_recovered = Frame(self.top_frame, bg='black', bd=0)
        self.top_frame_recovered.grid(column=2, row=0, sticky='w')

        # Loads and places the heart icon.
        icon_recovered = Image.open(f'.{os.sep}icons{os.sep}heart.png')
        icon_recovered = icon_recovered.resize((int(w/50), int(w/50)), Image.ANTIALIAS)
        render_recovered = ImageTk.PhotoImage(icon_recovered)
        self.icon_recovered_world = Label(self.top_frame_recovered, image=render_recovered, bg='black')
        self.icon_recovered_world.image = render_recovered
        self.icon_recovered_world.grid(column=0, row=0, sticky='w')
        self.world_recovered = Label(self.top_frame_recovered, text='0', fg='white', bg='black', font=("SFUIText", 14, "bold"))
        self.world_recovered.grid(column=1, row=0, sticky='w')

        # The inner bottom frame with russian Covid-19 cases.
        self.bottom_frame = Frame(self.covid_frame, bg='black', bd=0)
        self.bottom_frame.grid(column=0, row=1, sticky='w')

        # The leftmost frame inside the top frame to display the number of cases in Russia.
        self.bottom_frame_cases = Frame(self.bottom_frame, bg='black', bd=0)
        self.bottom_frame_cases.grid(column=0, row=0, sticky='w')

        # Loads and places the biohazard icon for the bottom frame.
        self.RUS = Label(self.bottom_frame_cases, text='RUS ', fg='white', bg='black', font=("SFUIText", 12, "bold"))
        self.RUS.grid(column=0, row=0, sticky='w')

        icon_cases_rus = Image.open(f'.{os.sep}icons{os.sep}biohazard.png')
        icon_cases_rus = icon_cases_rus.resize((int(w/65), int(w/65)), Image.ANTIALIAS)
        render_cases_rus = ImageTk.PhotoImage(icon_cases_rus)
        self.icon_cases_rus = Label(self.bottom_frame_cases, image=render_cases_rus, bg='black')
        self.icon_cases_rus.image = render_cases_rus
        self.icon_cases_rus.grid(column=1, row=0, sticky='w')

        self.rus_cases = Label(self.bottom_frame_cases, text='0', fg='white', bg='black', font=("SFUIText", 12, "bold"))
        self.rus_cases.grid(column=2, row=0, sticky='w')

        # Loads and places the scull icon for the bottom frame.
        icon_deaths_rus = Image.open(f'.{os.sep}icons{os.sep}dead.png')
        icon_deaths_rus = icon_deaths_rus.resize((int(w/65), int(w/65)), Image.ANTIALIAS)
        render_deaths_rus = ImageTk.PhotoImage(icon_deaths_rus)
        self.icon_deaths_rus = Label(self.bottom_frame_cases, image=render_deaths_rus, bg='black')
        self.icon_deaths_rus.image = render_deaths_rus
        self.icon_deaths_rus.grid(column=3, row=0, sticky='w')

        self.rus_deaths = Label(self.bottom_frame_cases, text='0', fg='white', bg='black', font=("SFUIText", 12, "bold"))
        self.rus_deaths.grid(column=4, row=0, sticky='w')

        # Loads and places the heart icon for the bottom frame.
        icon_recovered_rus = Image.open(f'.{os.sep}icons{os.sep}heart.png')
        icon_recovered_rus = icon_recovered_rus.resize((int(w/65), int(w/65)), Image.ANTIALIAS)
        render_recovered_rus = ImageTk.PhotoImage(icon_recovered_rus)
        self.icon_recovered_rus = Label(self.bottom_frame_cases, image=render_recovered_rus, bg='black')
        self.icon_recovered_rus.image = render_recovered_rus
        self.icon_recovered_rus.grid(column=5, row=0, sticky='w')

        self.rus_recovered = Label(self.bottom_frame_cases, text='0', fg='white', bg='black', font=("SFUIText", 12, "bold"))
        self.rus_recovered.grid(column=6, row=0, sticky='w')

        self.widget()

    def widget(self):
        if self.gesturesAssistant.is_face_detected == False:
            self.icon_cases_world.configure(image='')
            self.icon_deaths_world.configure(image='')
            self.icon_recovered_world.configure(image='')
            self.icon_cases_rus.configure(image='')
            self.icon_deaths_rus.configure(image='')
            self.icon_recovered_rus.configure(image='')
            self.world_cases.config(text='')
            self.world_deaths.config(text='')
            self.world_recovered.config(text='')
            self.rus_cases.config(text='')
            self.rus_deaths.config(text='')
            self.rus_recovered.config(text='')

        else:
            if len(self.parserBot.covid_figures) > 7:
                self.world_cases.config(text=f'{self.parserBot.covid_figures[0]} ')
                self.world_deaths.config(text=f'{self.parserBot.covid_figures[1]} ')
                self.world_recovered.config(text=self.parserBot.covid_figures[2])
                self.rus_cases.config(text=f'{self.parserBot.covid_figures[3]} ({self.parserBot.covid_figures[4]})  ')
                self.rus_deaths.config(text=f'{self.parserBot.covid_figures[5]} ({self.parserBot.covid_figures[6]})  ')
                self.rus_recovered.config(text=self.parserBot.covid_figures[7])
        self.world_cases.after(1000, self.widget)

if __name__ == '__main__':
    class ParserBot:
        def __init__(self):
            self.covid_figures = ['80000', '1521', '2342', '2', '+1', '0', '0', '0']
    class GesturesAssistant:
        def __init__(self):
            self.is_face_detected = True
    parserBot = ParserBot()
    gesturesAssistant = GesturesAssistant()
    window = Tk()
    window.title('Main Window')
    window.configure(bg='black')
    window.overrideredirect(True)
    w, h = window.winfo_screenwidth(), window.winfo_screenheight()
    window.geometry("%dx%d+0+0" % (w, h))
    a = Covid(window, parserBot, gesturesAssistant)
    window.mainloop()