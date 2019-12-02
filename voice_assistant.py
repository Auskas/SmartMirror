#! python3
# voice_assistant.py - voice assistant for my Smart Mirror project.

import logging
import speech_recognition as sr
import os
import sys
import threading

class VoiceAssistant():
    
    def __init__(self):
        self.r = sr.Recognizer()
        self.logger = logging.getLogger('Gesell.voice_assistant.VoiceAssistant')
        self.logger.info('Voice assistant has been initialized.')
        self.cmd = set()
        self.youtube = ('видео', 'смотреть', 'включи', 'проиграть', 'выведи на экран', 'загрузи',
                       'ютюб', 'ютуб', 'youtube')

    def assistant(self):
        while True:
            #print('Продолжаем!')
            self.myCommand()

    def myCommand(self):
        with sr.Microphone(sample_rate=16000, chunk_size=1024) as source:
            # Represents the minimum length of silence (in seconds) that will register as the end of a phrase (type: float).
            self.r.pause_threshold = 1
            # The duration parameter is the maximum number of seconds that it will dynamically adjust the threshold for before returning.
            #This value should be at least 0.5 in order to get a representative sample of the ambient noise.
            self.r.adjust_for_ambient_noise(source, duration=1)
            audio = self.r.listen(source)
        try:
            user_speech = self.r.recognize_google(audio, language = "ru-RU").lower()
            self.logger.debug(f'User said: {user_speech}')
            self.cmd_handler(user_speech)
        except sr.UnknownValueError:
            pass
            
    def cmd_handler(self, cmd):
        if cmd.find('полный экран') != -1 or cmd.find('весь экран') != -1 or cmd.find('развернуть') != -1:
            self.cmd.add('fullscreen')
        
        elif cmd.find('убрать') != -1 or cmd.find('в окно') != -1 or cmd.find('в угол') != -1 or cmd.find('свернуть') != -1:
            self.cmd.add('window')
        
        elif cmd.find('смотреть') != -1 or cmd.find('покажи') != -1 or cmd.find('включи') != -1:
            if cmd.find('смотреть') != -1:
                cmd = cmd[cmd.find('смотреть'):]
                cmd = cmd.replace('смотреть', '')
            elif cmd.find('покажи') != -1:
                cmd = cmd[cmd.find('покажи'):]
                cmd = cmd.replace('покажи', '')
            else:
                cmd = cmd[cmd.find('включи'):]
                cmd = cmd.replace('включи', '')
            self.cmd.add(f'play {cmd}')            

if __name__ == '__main__':
    assistant = VoiceAssistant()
    assistant.assistant()
