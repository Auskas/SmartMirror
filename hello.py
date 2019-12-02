#! python3
# hello.py - a Hello widget for my Smart Mirror project.
# Prints 'Hello' to the registered users captured in the camera.

from tkinter import *
import datetime
import time
import logging
from random import choice

class Hello:

    def __init__(self, frame, face_recognizer, clock, database):
        self.logger = logging.getLogger('Gesell.hello.Hello')
        self.logger.debug('Initializing an instance of Hello Widget...')
        self.face_recognizer = face_recognizer
        self.helloLbl = Label(frame, text='',  fg='lightblue', bg='black', font=("SF UI Display Semibold", 30))
        self.helloLbl.place(relx=0.5, rely=0.5, anchor='c')
        self.clock = clock
        self.compliment_anna = ('Потрясающе выглядишь', 'Ты как всегда прекрасна', 'Выглядишь на миллион долларов',
                                'Выглядишь блестяще', 'Ты самая красивая', 'Твоя красота сногсшибательна')
        self.names = {'Dmitry': 'Дмитрий', 'Anna': 'Анна', 'Yaroslav': 'Ярослав', 'Agniya': 'Агния'}
        self.logger.info('Hello Widget has been started.')
        self.users = () # the set contains of all people detected in front of the mirror.
        self.database = database
        self.hello_widget()
        
    def hello_widget(self):
        self.helloLbl.config(text='')
        key, greetings = self.part_of_the_day()
        for user in self.face_recognizer.current_users:
            if self.database.usersDatabase[user][key]:
                continue
            else:
                self.database.usersDatabase[user][key] = True
                if user == 'Anna':
                    self.helloLbl.config(text=f'{greetings} Анна! {choice(self.compliment_anna)}!')
                else:
                    self.helloLbl.config(text=f'{greetings} {self.names[user]}')
        self.helloLbl.after(3000, self.hello_widget)

    def part_of_the_day(self):
        if self.clock.current_date_and_time.hour < 6:
            return 'night', 'Доброй ночи'
        elif 10 >= self.clock.current_date_and_time.hour >= 6:
            return 'morning', 'Доброе утро'
        elif 16 >= self.clock.current_date_and_time.hour >= 11:
            return 'day', 'Добрый день'
        else:
            return 'evening', 'Добрый вечер'
        
            
