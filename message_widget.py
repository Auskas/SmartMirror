#!/usr/bin/python3
# message_widget.py - the message widget for my Smart Mirror project.

from tkinter import *    
import datetime
import logging

class MessageWidget:

    def __init__(self, frame, voiceAssistant, gesturesRecognizer):
        self.logger = logging.getLogger('Gesell.message_widget.MessageWidget')
        self.logger.debug('Initializing an instance of Message Widget...')
        font = 25
        self.messageMsg = Message(frame,  text='', fg='red', bg='black', font=("SFUIText", font, "bold"), width=17 * font)
        self.messageMsg.place(relx=0.5, rely=0.35, anchor=CENTER)
        self.voiceAssistant = voiceAssistant
        self.gesturesRecognizer = gesturesRecognizer
        self.logger.info('Message Widget has been created.')
        if self.gesturesRecognizer.camera_found:
            self.widget()
        else:
            self.camera_warning()
        
    def widget(self):
        if self.voiceAssistant.cmd['gesturesMode']:
            self.messageMsg.config(text=self.gesturesRecognizer.LABEL)
        self.messageMsg.after(500, self.widget)
    
    def camera_warning(self):
        self.messageMsg.config(text='Camera not found. Gestures control is DISABLED.')
        self.messageMsg.after(5000, self.clear_message)

    def clear_message(self):
        self.messageMsg.config(text='')
        self.messageMsg.after(1, self.widget)