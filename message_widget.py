#! python3
# message_widget.py - the message widget for my Smart Mirror project.
# Displays different messages for different users.

from tkinter import *    
import datetime
import logging

class MessageWidget:

    def __init__(self, frame, face_recognizer, clock, database):
        self.logger = logging.getLogger('Gesell.message_widget.MessageWidget')
        self.logger.debug('Initializing an instance of Message Widget...')
        self.messageMsg = Message(frame,  text='', fg='lightblue', bg='black', font=("SF UI Display Semibold", 18, "bold"), width=200, anchor=E)
        self.messageMsg.place(relx=0.97, rely=0.1, anchor='ne')
        self.face_recognizer = face_recognizer
        self.clock = clock
        self.face_recognizer = face_recognizer
        self.database = database
        self.logger.info('Message Widget has been created.')
        self.widget()
        

    def widget(self):
        for user in self.face_recognizer.current_users:
            if user == 'Anna':
                self.messageMsg.config(text='Вторник\n09:35 - 10:20   5б\n10:35 - 11:20   2а\n11:35 - 12:20   4г\n12:30 - 13:15   3э\n13:35 - 14:20   5а')
            elif user == 'Dmitry':
                self.messageMsg.config(text='Дмитрий, не забудь взять миллион долларов на завтра!')
        if len(self.face_recognizer.current_users) == 0:
                self.messageMsg.config(text='')
        self.messageMsg.after(2000, self.widget)
        
