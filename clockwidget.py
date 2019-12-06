#! python3
# clockwidget.py - creates widget and updates current time for my smart mirror project.

from tkinter import *
import datetime
import time
import logging

class Clock:

    def __init__(self, frame, database):
        self.logger = logging.getLogger('Gesell.clockwidget.Clock')
        self.logger.debug('Initializing an instance of Clock Widget...')
        self.timeLbl = Label(frame, text='', fg='lightblue', bg='black', font=("SF UI Display", 48))
        self.timeLbl.place(relx=0.03, rely=0.01)
        #self.timeLbl.grid(row=0, column=0, sticky='w', padx=10)
        self.dateLbl = Label(frame, text='', fg='lightblue', bg='black', font=("SF UI Display", 28))
        self.dateLbl.place(relx=0.03, rely=0.1)
        #self.dateLbl.grid(row=1, column=0, sticky='w', padx=10, ipady=7)
        self.months = {1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля', 5: 'мая', 6: 'июня',
                       7: 'июля', 8: 'августа', 9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'}
        self.weekdays = {0: 'Понедельник', 1: 'Вторник', 2: 'Среда', 3: 'Четверг', 4: 'Пятница', 5: 'Суббота', 6: 'Воскресенье'}
        self.logger.debug('Clock Widget has been created')
        self.current_date_and_time = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
        self.calendar_widget(self.current_date_and_time)
        self.database = database
        self.clock_widget()
        
    def clock(self):
        self.current_date_and_time = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
        current_time_str = self.current_date_and_time.strftime('%H:%M:%S')
        return current_time_str, self.current_date_and_time

    def clock_widget(self):
        current_time_str, current_date_and_time = self.clock()
        if current_time_str == '00:00:00':
            self.calendar_widget(current_date_and_time)
            # Resetting users' greetings for the next day.
            for user in self.database.usersDatabase:
                self.database.usersDatabase[user]['morning'] = False
                self.database.usersDatabase[user]['day'] = False
                self.database.usersDatabase[user]['evening'] = False
                self.database.usersDatabase[user]['night'] = False
        self.timeLbl.config(text=current_time_str)
        self.timeLbl.after(1000, self.clock_widget)

    def calendar_widget(self, current_date_and_time):
        days = current_date_and_time.day
        if days < 10:
            days = f'0{current_date_and_time.day}'
        else:
            days = str(days)
        weekday = self.weekdays[current_date_and_time.weekday()]
        month = self.months[current_date_and_time.month]
        current_date_str =  f'{weekday}, {days} {month}'
        self.dateLbl.config(text=current_date_str)
