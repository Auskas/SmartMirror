#! python3
# spartakwidget.py - a widget of the best FC in the world for my Smart Mirror project.

from tkinter import *
import os
import datetime
import time
import logging
from PIL import Image, ImageTk

class Spartak:

    def __init__(self, frame, nextgame, database, livescore, voiceAssistant, gesturesAssistant):
        
        self.logger = logging.getLogger('Gesell.spartakwidget.Spartak')
        self.logger.debug('Initializing an instance of Spartak Widget')

        # The frame for the icon and the text.
        self.widgetFrame = Frame(frame, bg='black', bd=0)
        self.widgetFrame.place(relx=0.05, rely=0.88)

        # FC Spartak Moscow icon.
        self.render = ImageTk.PhotoImage(Image.open(f'icons{os.sep}spartak_icon.jpg'))
        self.icon = Label(self.widgetFrame, image=self.render, bg='black')
        self.icon.image = self.render
        self.icon.pack(side=LEFT)

        # FC Spartak Moscow label: either the upcoming game and the coefficients or live score.
        self.teamLbl = Label(self.widgetFrame, text='', fg='lightblue', bg='black', font=("SFUIText", 18, "bold"))
        self.teamLbl.pack(side=LEFT)
        
        self.nextgame = nextgame
        self.database = database
        self.livescore = livescore
        self.voiceAssistant = voiceAssistant
        self.gesturesAssistant = gesturesAssistant
        self.goalshow = False
        self.hide_icon = True
        
        self.logger.debug('Spartak widget has just been initialized.')
        
        self.widget()

    def show_icon(self):
        #self.render = ImageTk.PhotoImage(Image.open('spartak_icon.jpg'))
        #self.icon = Label(self.widgetFrame, image=self.render, bg='black')
        #self.icon.image = self.render
        self.icon.config(image=self.render)
        self.hide_icon = False

    def widget(self):
        if self.gesturesAssistant.is_face_detected == False:
            self.teamLbl.config(text='', fg='red', font=("SFUIText", 32))
            self.icon.config(image='')
            self.hide_icon = True
            self.teamLbl.after(2000, self.widget)
        else:
            #self.icon.config(image=self.render)
            if self.database.teamDatabase['current_game'] == 'None':
                if self.voiceAssistant.cmd['spartak']:
                    nextgame_string = self.nextgame.nextgame_string
                    self.teamLbl.config(text=nextgame_string, fg='lightblue', font=("SFUIText", 16, "bold"))
                    if self.hide_icon:
                        self.show_icon()                    
                else:
                    self.teamLbl.config(text='', fg='lightblue', font=("SFUIText", 16, "bold"))
                    if self.hide_icon == False:
                        #self.icon.configure(image='')
                        self.icon.config(state='hidden')
                        self.hide_icon = True
            else:
                if self.voiceAssistant.cmd['spartak']:
                    if self.livescore.status != 'Перерыв':
                        status_string = f'{self.livescore.home_team} - {self.livescore.away_team}   {self.livescore.livescore}   {self.livescore.status}   {self.livescore.elapsed}\''
                    else:
                        status_string = f'{self.livescore.home_team} - {self.livescore.away_team}   {self.livescore.livescore}   {self.livescore.status}'
                        self.teamLbl.after(1000, self.widget)
                    self.teamLbl.config(text=status_string, fg='lightblue', font=("SFUIText", 16, "bold"))
                    if self.livescore.goal:
                        if self.goalshow:
                            self.teamLbl.config(text='ГОЛ!!!', fg='red', font=("SFUIText", 32, "bold"))
                            self.goalshow = False
                        else:
                            self.goalshow = True
                else:
                    self.teamLbl.config(text='', fg='red', font=("SFUIText", 32))
            self.teamLbl.after(1000, self.widget)
       
if __name__ == '__main__':
    class VoiceAssistant:
        def __init__(self):
            self.cmd = {'spartak': True}
    class GesturesAssistant:
        def __init__(self):
            self.is_face_detected = True
    class Nextgame:
        def __init__(self):
            self.nextgame_string = 'Спартак - Ливерпуль 31.02.2021'
    class Database:
        def __init__(self):
            self.teamDatabase = {'current_game': 'None'}
    class Livescore:
        def __init__(self):
            self.nothing = None
    voiceAssistant = VoiceAssistant()
    gesturesAssistant = GesturesAssistant()
    nextgame = Nextgame()
    database = Database()
    livescore = Livescore()
    window = Tk()
    window.title('Main Window')
    window.configure(bg='black')
    window.overrideredirect(True)
    w, h = window.winfo_screenwidth(), window.winfo_screenheight()
    window.geometry("%dx%d+0+0" % (w, h))
    a = Spartak(window, nextgame, database, livescore, voiceAssistant, gesturesAssistant)
    window.mainloop()
        
