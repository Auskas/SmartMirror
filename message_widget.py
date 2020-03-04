#!/usr/bin/python3
# message_widget.py - the message widget for my Smart Mirror project.

from tkinter import *    
import datetime
import logging

class MessageWidget:

    def __init__(self, frame, voiceAssistant, gesturesRecognizer):
        self.logger = logging.getLogger('Gesell.message_widget.MessageWidget')
        self.logger.debug('Initializing an instance of Message Widget...')
        self.messageMsg = Message(frame,  text='', fg='lightblue', bg='black', font=("SF UI Display Semibold", 25, "bold"), width=200)
        self.messageMsg.place(relx=0.5, rely=0.35, anchor=CENTER)
        self.voiceAssistant = voiceAssistant
        self.gesturesRecognizer = gesturesRecognizer
        self.logger.info('Message Widget has been created.')
        self.widget()
        
    def widget(self):
        if self.voiceAssistant.cmd['gesturesMode']:
            self.messageMsg.config(text=self.gesturesRecognizer.LABEL)
        self.messageMsg.after(500, self.widget)
        
