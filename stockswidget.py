#! python3
# stockswidget.py - module creates exchange rates and oil price widget.

from tkinter import *    
import datetime
import logging

class Stocks:

    def __init__(self, frame, yandexbot, voiceAssistant):
        self.logger = logging.getLogger('Gesell.stockswidget.Stocks')
        self.logger.debug('Initializing an instance of Stocks Widget...')
        self.yandexBot = yandexbot
        self.voiceAssistant = voiceAssistant
        self.stocksLbl = Label(frame, text='', fg='lightblue', bg='black', font=("SF UI Display Semibold", 18, "bold"))
        self.stocksLbl.place(relx=0.97, rely=0.01, anchor='ne')
        #self.face_recognizer = face_recognizer
        self.logger.debug('Stocks Widget has been created.')
        self.widget()

    def widget(self):
        new_rates = self.yandexBot.rates_string
        if new_rates == '':
            self.stocksLbl.after(2000, self.widget)
        elif new_rates != '' and self.voiceAssistant.cmd['stocks']:
            self.stocksLbl.config(text=new_rates)
        else:
            self.stocksLbl.config(text='')
        self.stocksLbl.after(2000, self.widget)
            

            
        
__version__ = '0.01' # 20.11.2019


