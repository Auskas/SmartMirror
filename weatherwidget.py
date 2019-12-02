#! python3
# weatherwidget.py - a weather widget for my Smart Mirror project.

from tkinter import *
import requests
import datetime
import time
import logging
import os
from PIL import Image, ImageTk

class Weather:

    def __init__(self, frame):
        self.logger = logging.getLogger('Gesell.weatherwidget.Weather')
        self.logger.debug('Initializing an instance of Weather Widget...')
        self.frame = frame
        try:
            with open("weathertoken.txt") as f:
                self.key = f.read().strip()
                self.logger.debug('Weather token has been obtained from the file.')
        except Exception as error:
            self.logger.debug(f'Cannot get Weather token from the file: {error}')
            pass
        self.lat = '55.716848' # latitude of the forecast
        self.lon = '37.882962' # longitude of the forecast
        self.lang = 'ru_RU'    # language of the reply
        self.payload = payload = {'lat': self.lat, 'lon': self.lon, 'lang': self.lang}
        self.headers = {'X-Yandex-API-Key': self.key}
        self.url = 'https://api.weather.yandex.ru/v1/informers?'
        self.wind = {'nw': 'северо-западный', 'n': 'северный', 's': 'южный', 'w': 'западный',
                     'e': 'востончый', 'ne': 'северо-восточный', 'sw': 'юго-западный', 'se': 'юго-восточный'}

        self.weather_frame = Frame(frame, bg='black', bd=0)
        self.weather_frame.place(relx=0.03, rely=0.2)

        self.topframe_inside = Frame(self.weather_frame, bg='black', bd=0)
        self.topframe_inside.grid(column=0, row=0, sticky='w')

        self.bottomframe_inside = Frame(self.weather_frame, bg='black', bd=0)
        self.bottomframe_inside.grid(column=0, row=1, sticky='w')

        self.titleLbl = Label(self.topframe_inside, text="Москва", fg='lightblue', bg='black', font=("SF UI Display Semibold", 13, "bold"))
        self.titleLbl.pack(side=LEFT)

        render = ImageTk.PhotoImage(Image.open(f'.{os.sep}Yandex_Weather{os.sep}bkn_+ra_d.png'))
        self.icon = Label(self.bottomframe_inside, image=render, bg='black')
        self.icon.image = render
        self.icon.pack(side=LEFT)

        self.degrees = Label(self.bottomframe_inside, text="-5°C", fg='lightblue', bg='black', font=("SF UI Display Black", 22, "bold"))
        self.degrees.pack(side=LEFT)

        self.next_frame = Frame(self.bottomframe_inside, bg='black', bd=0)
        self.next_frame.pack(side=LEFT)

        self.next_frame_top = Frame(self.next_frame, bg='black', bd=0)
        self.next_frame_top.grid(column=0, row=0, sticky='w')

        self.next_frame_bottom = Frame(self.next_frame, bg='black', bd=0)
        self.next_frame_bottom.grid(column=0, row=1, sticky='w')

        self.next_forecast = Label(self.next_frame_top, text="Днём -3°C", fg='lightblue', bg='black', font=("SF UI Display Semibold", 12, "bold"))
        self.next_forecast.pack(side = LEFT)

        self.next_next_forecast = Label(self.next_frame_bottom, text="Вечером -6°C", fg='lightblue', bg='black', font=("SF UI Display Semibold", 12, "bold"))
        self.next_next_forecast.pack(side = LEFT)
        
        self.logger.debug('Weather Widget has been initialized.')
        self.widget()

    def widget(self):
        forecast = self.get_weather()
        print(forecast)
        if forecast != None:
            temp_now = str(forecast['fact']['temp'])
            weather_icon = forecast['fact']['icon']
            
            render = ImageTk.PhotoImage(Image.open(f'.{os.sep}Yandex_Weather{os.sep}{weather_icon}.png'))
            self.icon.configure(image=render)
            self.icon.image = render
            
            temp_next = str(forecast['forecast']['parts'][0]['temp_avg'])
            part_next = forecast['forecast']['parts'][0]['part_name']
            
            temp_next_next = str(forecast['forecast']['parts'][1]['temp_avg'])

            if part_next == 'night':
                part_next, part_next_next  = 'Ночью', 'Утром'
            elif part_next == 'morning':
                part_next, part_next_next  = 'Утром', 'Днём'
            elif part_next == 'day':
                part_next, part_next_next  = 'Днём', 'Вечером'
            else:
                part_next, part_next_next  = 'Вечером', 'Ночью'
            self.degrees.config(text=f'{temp_now}°С')
            self.next_forecast.config(text=f'{part_next} {temp_next}°С')
            self.next_next_forecast.config(text=f'{part_next_next} {temp_next_next}°С')
        self.degrees.after(3600000, self.widget)

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
    window = Tk()
    window.title('Main Window')
    window.configure(bg='black')
    window.overrideredirect(True)
    w, h = window.winfo_screenwidth(), window.winfo_screenheight()
    window.geometry("%dx%d+0+0" % (w, h))
    a = Weather(window)
    
