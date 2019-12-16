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
        #self.r.energy_threshold = 350
        self.logger = logging.getLogger('Gesell.voice_assistant.VoiceAssistant')
        self.logger.info('Voice assistant has been initialized.')
        self.cmd = {'youtube' : set(), 'weather': True, 'stocks': True,
                    'marquee': True, 'spartak': True, 'clock': True}

    def assistant(self):
        while True:
            #print('Продолжаем!')
            self.myCommand()

    def myCommand(self):
        with sr.Microphone(sample_rate=16000, chunk_size=1024) as source:
            # Represents the minimum length of silence (in seconds) that will register as the end of a phrase (type: float).
            self.r.pause_threshold = 2
            # The duration parameter is the maximum number of seconds that it will dynamically adjust the threshold for before returning.
            #This value should be at least 0.5 in order to get a representative sample of the ambient noise.
            #self.r.dynamic_energy_threshold = False
            self.r.adjust_for_ambient_noise(source, duration=0.5)
            try:
                print('ГОВОРИТЕ!!!')
                audio = self.r.listen(source,timeout=6)
            # Catches the exception when there is nothing said during speech recognition.
            except sr.WaitTimeoutError:
                self.logger.debug('Timeout: no speech has been registred.')
                return None
        try:
            user_speech = self.r.recognize_google(audio, language = "ru-RU").lower()
            self.logger.debug(f'User said: {user_speech}')
            return self.cmd_handler(user_speech)
        except sr.UnknownValueError:
            print('Cannot recognize')
            return None
            
    def cmd_handler(self, cmd):
        if cmd.find('часы') != -1 and (cmd.find('убрать') != -1 or cmd.find('убери') != -1 or
                                       cmd.find('скрыть') != -1 or cmd.find('скрой') != -1):
            self.cmd['clock'] = False
        
        elif cmd.find('часы') != -1 and (cmd.find('показать') != -1 or cmd.find('вывести') != -1 or
                                         cmd.find('покажи') != -1 or cmd.find('выведи') != -1):
            self.cmd['clock'] = True

        elif cmd.find('погод') != -1 and (cmd.find('убрать') != -1 or cmd.find('убери') != -1 or
                                       cmd.find('скрыть') != -1 or cmd.find('скрой') != -1):
            self.cmd['weather'] = False
        
        elif cmd.find('погод') != -1 and (cmd.find('показать') != -1 or cmd.find('вывести') != -1 or
                                         cmd.find('покажи') != -1 or cmd.find('выведи') != -1):
            self.cmd['weather'] = True
            
        elif cmd.find('курс') != -1 and (cmd.find('убрать') != -1 or cmd.find('убери') != -1 or
                                       cmd.find('скрыть') != -1 or cmd.find('скрой') != -1):
            self.cmd['stocks'] = False
        
        elif cmd.find('курс') != -1 and (cmd.find('показать') != -1 or cmd.find('вывести') != -1 or
                                         cmd.find('покажи') != -1 or cmd.find('выведи') != -1):
            self.cmd['stocks'] = True
            
        elif cmd.find('спартак') != -1 and (cmd.find('убрать') != -1 or cmd.find('убери') != -1 or
                                       cmd.find('скрыть') != -1 or cmd.find('скрой') != -1):
            self.cmd['spartak'] = False
        
        elif cmd.find('спартак') != -1 and (cmd.find('показать') != -1 or cmd.find('вывести') != -1 or
                                         cmd.find('покажи') != -1 or cmd.find('выведи') != -1):
            self.cmd['spartak'] = True            
            
        elif cmd.find('полный экран') != -1 or cmd.find('весь экран') != -1 or cmd.find('развернуть') != -1 or cmd.find('fullscreen') != -1:
            self.cmd['youtube'].add('fullscreen')
        
        elif (cmd.find('убрать') != -1 or cmd.find('окно') != -1 or cmd.find('в угол') != -1 or cmd.find('свернуть') != -1 or
              cmd.find('window') != -1):
            self.cmd['youtube'].add('window')
            
        elif (cmd.find('видео') != -1 or cmd.find('video') != -1 or cmd.find('playback') != -1) and (cmd.find('стоп') != -1
              or cmd.find('остановить') != -1 or cmd.find('stop') != -1):
            self.cmd['youtube'].add('playback stop')
        
        elif (cmd.find('видео') != -1 or cmd.find('video') != -1 or cmd.find('playback') != -1) and (cmd.find('пауза') != -1
              or cmd.find('pause') != -1):
            self.cmd['youtube'].add('playback pause')
        
        elif (cmd.find('видео') != -1 or cmd.find('video') != -1 or cmd.find('playback') != -1) and (cmd.find('возобновить') != -1
              or cmd.find('play') != -1 or cmd.find('продолжить') != -1 or cmd.find('resume') != -1):
            self.cmd['youtube'].add('playback resume')
            
        elif (cmd.find('строка') != -1 or cmd.find('новост') != -1) and (cmd.find('убрать') != -1 or
              cmd.find('убери') != -1 or cmd.find('скрыть') != -1 or cmd.find('скрой') != -1):
            self.cmd['marquee'] = False
        
        elif (cmd.find('строка') != -1 or cmd.find('новост') != -1) and (cmd.find('показать') != -1
              or cmd.find('вывести') != -1 or cmd.find('покажи') != -1 or cmd.find('выведи') != -1):
            self.cmd['marquee'] = True
        
        elif (cmd.find('смотреть') != -1 or cmd.find('покажи') != -1 or cmd.find('включи') != -1
              or cmd.find('watch') != -1 or cmd.find('youtube') != -1 or cmd.find('show me') != -1):
            if cmd.find('смотреть') != -1:
                cmd = cmd[cmd.find('смотреть'):]
                cmd = cmd.replace('смотреть', '')
            elif cmd.find('покажи') != -1:
                cmd = cmd[cmd.find('покажи'):]
                cmd = cmd.replace('покажи', '')
            else:
                cmd = cmd[cmd.find('включи'):]
                cmd = cmd.replace('включи', '')
            self.cmd['youtube'].add(f'video search {cmd}')
        if len(self.cmd) > 0:
            self.logger.debug(f'The following phrases have been detected: {self.cmd}')
        return cmd            

if __name__ == '__main__':
    assistant = VoiceAssistant()
    assistant.assistant()
