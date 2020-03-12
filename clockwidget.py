#!/usr/bin/python3
# clockwidget.py - creates a clock and a calendar widgets and updates the current time and date.

from tkinter import *
import datetime
import time
import logging

class Clock:

    def __init__(self, frame, database, voiceAssistant, gesturesAssistant):
        self.logger = logging.getLogger('Gesell.clockwidget.Clock')

        if __name__ == '__main__': # Creates a logger if the module is called directly.
            ch = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.setLevel(logging.DEBUG)
            self.logger.addHandler(ch)

        self.logger.debug('Initializing an instance of Clock Widget...')
        
        # An instance of VoiceAssistant is used to determine either to show or conceal the widgets.
        self.voiceAssistant = voiceAssistant
        self.gesturesAssistant = gesturesAssistant

        self.timeLbl = Label(frame, text='', fg='lightblue', bg='black', font=("SFUIText", 48, "bold"))
        self.timeLbl.place(relx=0.05, rely=0.05)

        self.dateLbl = Label(frame, text='', fg='lightblue', bg='black', font=("SFUIText", 28, "bold"))
        self.dateLbl.place(relx=0.05, rely=0.15)

        self.months = {1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля', 5: 'мая', 6: 'июня',
                       7: 'июля', 8: 'августа', 9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'}
        self.weekdays = {0: 'Понедельник', 1: 'Вторник', 2: 'Среда', 3: 'Четверг', 4: 'Пятница', 5: 'Суббота', 6: 'Воскресенье'}
        
        self.current_date_and_time = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
        self.calendar_widget(self.current_date_and_time)

        # An instanse of Database is used to reset the status of greetings when a new day begins.
        # Currently that functionality is not implemented.
        self.database = database

        self.logger.debug('Clock and Calendar widgets have been created.')
        self.clock_widget()
        
    def clock(self):
        """ Determines the current date and time, returns the datetime object as well as 
            the current time as a string in the format HH:MM:SS."""
        self.current_date_and_time = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
        current_time_str = self.current_date_and_time.strftime('%H:%M:%S')
        return current_time_str, self.current_date_and_time

    def clock_widget(self):
        """ Updates the calendar widget at midnight.
            Updates the clock widget every second."""
        if self.gesturesAssistant.is_face_detected == False:
            self.timeLbl.config(text='')
            self.dateLbl.config(text='')
            self.timeLbl.after(2000, self.clock_widget)
        else:
            current_time_str, current_date_and_time = self.clock()

            if current_time_str == '00:00:00':
                self.calendar_widget(current_date_and_time)
                # Resetting users' greetings for the next day.
                for user in self.database.usersDatabase:
                    self.database.usersDatabase[user]['morning'] = False
                    self.database.usersDatabase[user]['day'] = False
                    self.database.usersDatabase[user]['evening'] = False
                    self.database.usersDatabase[user]['night'] = False

            # The following condition checks if the user decides to show or conceal the clock widget.
            if self.voiceAssistant.cmd['clock']:
                self.timeLbl.config(text=current_time_str)
                self.dateLbl.config(text=self.current_date_str)

            else:
                self.timeLbl.config(text='')
                self.dateLbl.config(text='')
            self.timeLbl.after(1000, self.clock_widget)

    def calendar_widget(self, current_date_and_time):
        """ Gets the current date and time object. If the day date is less than 10 adds a leading zero
            in order to maintain the same string date length. 
            Assigns to dateLbl the current date in the format {weekday}, DD {month}."""
        days = current_date_and_time.day
        # The following condition checks if it is necessary to put a zero in front of the date digit.
        #if days < 10:
            #days = f'0{current_date_and_time.day}'
        #else:
            #days = str(days)
        days = str(days)
        # Translates the weekday as a digit into the name of the weekday.
        weekday = self.weekdays[current_date_and_time.weekday()]
        # Translates the month number into the name of the month.
        month = self.months[current_date_and_time.month]
        self.current_date_str =  f'{weekday}, {days} {month}'
        self.dateLbl.config(text=self.current_date_str)

if __name__ == '__main__':
    """ For testing purposes."""
    class VoiceAssistant:
        def __init__(self):
            self.cmd = {'clock': True}

    class Database:
        def __init__(self):
            self.usersDatabase = {
                'Dmitry': {'morning': False, 'day': False, 'evening': False, 'night': False},
                'Anna': {'morning': False, 'day': False, 'evening': False, 'night': False},
                'Yaroslav': {'morning': False, 'day': False, 'evening': False, 'night': False},
                'Agniya': {'morning': False, 'day': False, 'evening': False, 'night': False}
                }

    class GesturesAssistant:
        def __init__(self):
            self.is_face_detected = True

    database = Database()
    voiceAssistant = VoiceAssistant()
    gesturesAssistant = GesturesAssistant()
    window = Tk()
    window.title('Main Window')
    window.configure(bg='black')
    window.overrideredirect(True)
    w, h = window.winfo_screenwidth(), window.winfo_screenheight()
    window.geometry("%dx%d+0+0" % (w, h))
    a = Clock(window, database, voiceAssistant, gesturesAssistant)
    window.mainloop()