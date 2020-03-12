#!/usr/bin/python3
# weatherwidget.py - a weather widget for my Smart Mirror project.

from tkinter import *
import requests
import datetime
import logging
import os
from PIL import Image, ImageTk

class Weather:

    def __init__(self, frame, voiceAssistant, gesturesAssistant):
        self.logger = logging.getLogger('Gesell.weatherwidget.Weather')

        if __name__ == '__main__': # Creates a logger if the module is called directly.
            ch = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.setLevel(logging.DEBUG)
            self.logger.addHandler(ch)

        self.logger.debug('Initializing an instance of Weather Widget...')
        self.voiceAssistant = voiceAssistant
        self.gesturesAssistant = gesturesAssistant
        self.frame = frame
        try:
            with open("weathertoken.txt") as f:
                self.key = f.read().strip()
                self.logger.debug('Weather token has been obtained from the file.')
        except Exception as error:
            self.logger.debug(f'Cannot get Weather token from the file: {error}')
            return None

        self.lat = '55.716848' # latitude of the forecast (Moscow)
        self.lon = '37.882962' # longitude of the forecast (Moscow)
        self.lang = 'ru_RU'    # language of the reply (Russian)
        self.payload = {'lat': self.lat, 'lon': self.lon, 'lang': self.lang}
        self.headers = {'X-Yandex-API-Key': self.key}
        self.url = 'https://api.weather.yandex.ru/v1/informers?'
        self.wind = {'nw': 'северо-западный', 'n': 'северный', 's': 'южный', 'w': 'западный',
                     'e': 'востончый', 'ne': 'северо-восточный', 'sw': 'юго-западный', 'se': 'юго-восточный'}

        # The main frame of the widget.
        self.weather_frame = Frame(frame, bg='black', bd=0)
        self.weather_frame.place(relx=0.05, rely=0.25)

        # The inner top frame with the name of the city.
        self.topframe_inside = Frame(self.weather_frame, bg='black', bd=0)
        self.topframe_inside.grid(column=0, row=0, sticky='w')

        # The inner bottom frame where all the weather data is displayed.
        self.bottomframe_inside = Frame(self.weather_frame, bg='black', bd=0)
        self.bottomframe_inside.grid(column=0, row=1, sticky='w')

        self.titleLbl = Label(self.topframe_inside, text="Москва", fg='lightblue', bg='black', font=("SFUIText", 22, "bold"))
        self.titleLbl.pack(side=LEFT)

        # The icon of the current weather taken from the Yandex_Weather folder.
        # It is placed the leftmost inside the inner bottom frame.
        render = ImageTk.PhotoImage(Image.open(f'.{os.sep}Yandex_Weather{os.sep}bkn_+ra_d.png'))
        self.icon = Label(self.bottomframe_inside, image=render, bg='black')
        self.icon.image = render
        self.icon.pack(side=LEFT)

        # The current temperature frame placed to the right of the weather icon.
        self.degrees = Label(self.bottomframe_inside, text="-5°C", fg='lightblue', bg='black', font=("SFUIText", 22, "bold"))
        self.degrees.pack(side=LEFT)

        # The forecast frame that is placed to the right of the current temperature frame.
        self.next_frame = Frame(self.bottomframe_inside, bg='black', bd=0)
        self.next_frame.pack(side=LEFT)

        # The top frame inside the forecast frame where the next period temperature is displayed.
        self.next_frame_top = Frame(self.next_frame, bg='black', bd=0)
        self.next_frame_top.grid(column=0, row=0, sticky='w')

        # The bottom frame inside the forecast frame where the second upcoming temperature period is shown.
        self.next_frame_bottom = Frame(self.next_frame, bg='black', bd=0)
        self.next_frame_bottom.grid(column=0, row=1, sticky='w')

        self.next_forecast = Label(self.next_frame_top, text="Днём -3°C", fg='lightblue', bg='black', font=("SFUIText", 12, "bold"))
        self.next_forecast.pack(side = LEFT)

        self.next_next_forecast = Label(self.next_frame_bottom, text="Вечером -6°C", fg='lightblue', bg='black', font=("SFUIText", 12, "bold"))
        self.next_next_forecast.pack(side = LEFT)
        
        # The following instance variable is used to determine when to update the weather.
        self.seconds_counter = 3601
        
        self.logger.debug('Weather Widget has been initialized.')
        self.widget()

    def widget(self):
        if self.gesturesAssistant.is_face_detected == False:
            self.degrees.config(text='')
            self.next_forecast.config(text='')
            self.next_next_forecast.config(text='')
            self.titleLbl.config(text='')
            self.icon.configure(image='')
            self.degrees.after(2000, self.widget)
        else:
            # Special weather forecast for April Fools' Day.
            current_time = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
            if current_time.month == 4 and current_time.day == 1 and self.seconds_counter > 3600:
                self.forecast = {'fact': {'temp': -1, 'icon': 'fct_+sn'},
                            'forecast': {'parts': [{'temp_avg': -5,
                                                    'part_name': 'evening'},
                                                   {'temp_avg': -8,
                                                    'part_name': 'night'}]}}
                self.seconds_counter = 0

            # The weather forecast is updated each hour.
            elif self.seconds_counter > 3600:
                self.forecast = self.get_weather()
                self.seconds_counter = 0

            # The following condition is used to show the widget.
            if self.forecast != None and self.voiceAssistant.cmd['weather']:
                self.titleLbl.config(text='Москва')
                temp_now = str(self.forecast['fact']['temp'])
                weather_icon = self.forecast['fact']['icon']
                
                render = ImageTk.PhotoImage(Image.open(f'.{os.sep}Yandex_Weather{os.sep}{weather_icon}.png'))
                self.icon.configure(image=render)
                self.icon.image = render
                
                temp_next = str(self.forecast['forecast']['parts'][0]['temp_avg'])
                part_next = self.forecast['forecast']['parts'][0]['part_name']
                
                temp_next_next = str(self.forecast['forecast']['parts'][1]['temp_avg'])

                # The following conditions are for determining the names of the next two part of a day.
                if part_next == 'night':
                    part_next, part_next_next  = 'Ночью', 'утром'
                elif part_next == 'morning':
                    part_next, part_next_next  = 'Утром', 'днём'
                elif part_next == 'day':
                    part_next, part_next_next  = 'Днём', 'вечером'
                else:
                    part_next, part_next_next  = 'Вечером', 'ночью'
                    
                self.degrees.config(text=f'{temp_now}° ')
                self.next_forecast.config(text=f'{part_next} {temp_next},')
                self.next_next_forecast.config(text=f'{part_next_next} {temp_next_next}')

            # Conceals the widget if the proper voice command is given.
            else:
                self.degrees.config(text='')
                self.next_forecast.config(text='')
                self.next_next_forecast.config(text='')
                self.titleLbl.config(text='')
                self.icon.configure(image='')

            # Adds a second to the counter and call the method again in a second.
            self.seconds_counter += 1
            self.degrees.after(1000, self.widget)
        

    def get_weather(self):
        try:
            res = requests.request(method='GET', url=self.url, params=self.payload, headers=self.headers)
            self.logger.debug('Got a reply from Yandex Weather API.')
        except Exception as error:
            self.logger.error(f'Cannot get a reply from Yandex Weather API: {error}')
            return None
        try:
            forecast = res.json()
            self.logger.debug('Got JSON data from the reply.')
            return forecast
        except Exception as error:
            self.logger.error(f'JSON data is absent in the reply.')
            return None
                                 
                                 

if __name__ == '__main__':
    class VoiceAssistant:
        def __init__(self):
            self.cmd = {'weather': True}

    class GesturesAssistant:
        def __init__(self):
            self.is_face_detected = True

    voiceAssistant = VoiceAssistant()
    gesturesAssistant = GesturesAssistant()
    window = Tk()
    window.title('Main Window')
    window.configure(bg='black')
    window.overrideredirect(True)
    w, h = window.winfo_screenwidth(), window.winfo_screenheight()
    window.geometry("%dx%d+0+0" % (w, h))
    a = Weather(window, voiceAssistant, gesturesAssistant)
    window.mainloop()



