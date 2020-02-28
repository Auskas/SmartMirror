#! python3
# stockswidget.py - module creates the exchange rates and oil price widget.

from tkinter import *    
import datetime
import logging

class Stocks:

    def __init__(self, frame, yandexbot, voiceAssistant):
        self.logger = logging.getLogger('Gesell.stockswidget.Stocks')

        if __name__ == '__main__': # Creates a logger if the module is called directly.
            ch = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.setLevel(logging.DEBUG)
            self.logger.addHandler(ch)

        self.logger.debug('Initializing an instance of Stocks Widget...')
        self.yandexBot = yandexbot
        self.voiceAssistant = voiceAssistant
        self.stocksLbl = Label(frame, text='', fg='lightblue', bg='black', font=("SF UI Display Semibold", 18, "bold"))
        self.stocksLbl.place(relx=0.97, rely=0.01, anchor='ne')
        self.logger.debug('Stocks Widget has been created.')
        self.widget()

    def widget(self):
        """ Updates the widget every minute. Determines if the user decides to show or conceal the widget.
            There is a special string for April's Fool day."""

        current_time = datetime.datetime.utcnow() + datetime.timedelta(hours=3)

        # Special stocks ticker for April Fools' Day.
        if current_time.month == 4 and current_time.day == 1:
            new_rates = '$ 31.3↓   € 38.1↓   Brent 123.7↑'

        # Regular update for the stocks.
        else:
            new_rates = self.yandexBot.rates_string
        
        # Cannot get the last exchange rates.
        if new_rates == '':
            self.stocksLbl.config(text='')

        elif new_rates != '' and self.voiceAssistant.cmd['stocks']:
            self.stocksLbl.config(text=new_rates)

        # The user decides to conceal the widget.
        else:
            self.stocksLbl.config(text='')

        self.stocksLbl.after(60000, self.widget)
            
if __name__ == '__main__':
    """ For testing purposes."""
    class VoiceAssistant:
        def __init__(self):
            self.cmd = {'stocks': True}

    class YandexBot:
        def __init__(self):
            self.rates_string = '$ 31.3↓   € 38.1↓   Brent 123.7↑'

    voiceAssistant = VoiceAssistant()
    yandexBot = YandexBot()
    window = Tk()
    window.title('Main Window')
    window.configure(bg='black')
    window.overrideredirect(True)
    w, h = window.winfo_screenwidth(), window.winfo_screenheight()
    window.geometry("%dx%d+0+0" % (w, h))
    a = Stocks(window, yandexBot, voiceAssistant)
    window.mainloop()


