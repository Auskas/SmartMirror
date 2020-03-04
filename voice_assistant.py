#! python3
# voice_assistant.py - voice assistant for my Smart Mirror project.

import logging
import speech_recognition as sr

class VoiceAssistant():
    
    def __init__(self):
        #self.r.energy_threshold = 350
        self.logger = logging.getLogger('Gesell.voice_assistant.VoiceAssistant')
        self.r = sr.Recognizer()
        self.logger.info('Voice assistant has been initialized.')
        self.cmd = {'youtube' : set(), 'weather': True, 'stocks': True,
                    'marquee': True, 'spartak': True, 'clock': True,
                    'gesturesMode': False}
        self.hide_commands = ('убрать', 'убери', 'скрыть', 'скрой', 
                              'закрыть', 'закрой', 'выключи', 'выключить', 
                              'hide', 'conceal', ' off', 'remove')
        self.show_commands = ('показать', 'покажи', 'вывести', 'выведи',
                              'открой', 'открыть', 'включи', 'включить', 
                              'show', 'open', ' on', 'watch', 'play')

    def assistant(self):
        while True:
            self.myCommand()

    def myCommand(self):
        with sr.Microphone(sample_rate=16000, chunk_size=1024) as source:
            # Represents the minimum length of silence (in seconds) that will register as the end of a phrase (type: float).
            self.r.pause_threshold = 1
            # The duration parameter is the maximum number of seconds that it will dynamically adjust the threshold for before returning.
            #This value should be at least 0.5 in order to get a representative sample of the ambient noise.
            #self.r.dynamic_energy_threshold = False
            self.r.adjust_for_ambient_noise(source, duration=1)
            try:
                print('ГОВОРИТЕ!!!')
                audio = self.r.listen(source,timeout=6)
            # Catches the exception when there is nothing said during speech recognition.
            except sr.WaitTimeoutError:
                self.logger.debug('Timeout: no speech has been registred.')
                return None
        try:
            user_speech = self.r.recognize_google(audio, language = "en-EN").lower()
            self.logger.debug(f'User said: {user_speech}')
            return self.cmd_handler(user_speech)
        except sr.UnknownValueError:
            print('Cannot recognize')
            return None
            
    def cmd_handler(self, cmd):
        """ Gets a string of recognized speech as cmd. 
            Checks if there are any sort of commands in it.
            Modifies self.cmd according to the detected commands."""

        if self.second_part_command(cmd) == False and \
            (
            cmd.find('все виджеты') != -1 or \
            cmd.find('all the widgets') != -1 or \
            cmd.find('all widgets') or \
            cmd.find('всю графику') != -1 or \
            cmd.find('всё') != -1
            ):

            (
            self.cmd['clock'], 
            self.cmd['spartak'], 
            self.cmd['marquee'],
            self.cmd['stocks'], 
            self.cmd['weather']
            ) = False, False, False, False, False
            self.cmd['youtube'].add('playback stop')

        elif self.second_part_command(cmd) and \
            (
            cmd.find('все виджеты') != -1 or \
            cmd.find('all the widgets') != -1 or \
            cmd.find('всю графику') != -1 or \
            cmd.find('всё') != -1
            ):

            (
            self.cmd['clock'], 
            self.cmd['spartak'], 
            self.cmd['marquee'],
            self.cmd['stocks'], 
            self.cmd['weather']
            ) = True, True, True, True, True
            self.cmd['youtube'].add('playback resume')
            
        elif cmd.find('часы') != -1 and self.second_part_command(cmd) == False:
            self.cmd['clock'] = False

        elif cmd.find('часы') != -1 and self.second_part_command(cmd):
            self.cmd['clock'] = True

        elif cmd.find('погод') != -1 and self.second_part_command(cmd) == False:
            self.cmd['weather'] = False

        elif cmd.find('погод') != -1 and self.second_part_command(cmd):
            self.cmd['weather'] = True
            
        elif cmd.find('курс') != -1 and self.second_part_command(cmd) == False:
            self.cmd['stocks'] = False

        elif cmd.find('курс') != -1 and self.second_part_command(cmd):
            self.cmd['stocks'] = True
            
        elif cmd.find('спартак') != -1 and self.second_part_command(cmd) == False:
            self.cmd['spartak'] = False

        elif cmd.find('спартак') != -1 and self.second_part_command(cmd):
            self.cmd['spartak'] = True
            
        elif self.second_part_command(cmd) == False and \
            (cmd.find('строк') != -1 or cmd.find('новост') != -1):
            self.cmd['marquee'] = False

        elif self.second_part_command(cmd) and \
            (cmd.find('строка') != -1 or cmd.find('новост') != -1):
            self.cmd['marquee'] = True
            
        elif cmd.find('полный экран') != -1 or \
             cmd.find('весь экран') != -1 or \
             cmd.find('развернуть') != -1 or \
             cmd.find('full screen') != -1 or \
             cmd.find('fullscreen') != -1:
            self.cmd['youtube'].add('fullscreen')
        
        elif cmd.find('убрать') != -1 or \
             cmd.find('окно') != -1 or \
             cmd.find('в угол') != -1 or \
             cmd.find('свернуть') != -1 or \
             cmd.find('window') != -1:
            self.cmd['youtube'].add('window')
            
        elif (
             cmd.find('видео') != -1 or \
             cmd.find('video') != -1 or \
             cmd.find('playback') != -1
             ) and \
             (
             cmd.find('стоп') != -1 or \
             cmd.find('остановить') != -1 or \
             cmd.find('stop') != -1
             ):
            self.cmd['youtube'].add('playback stop')
        
        elif (
            cmd.find('видео') != -1 or \
            cmd.find('video') != -1 or \
            cmd.find('playback') != -1
            ) and \
            (
            cmd.find('пауза') != -1 or \
            cmd.find('pause') != -1
            ):
            self.cmd['youtube'].add('playback pause')
        
        elif (
            cmd.find('видео') != -1 or \
            cmd.find('video') != -1 or \
            cmd.find('playback') != -1
            ) and \
            (
            cmd.find('возобновить') != -1 or \
            cmd.find('play') != -1 or \
            cmd.find('продолжить') != -1 or \
            cmd.find('resume') != -1
            ):
            self.cmd['youtube'].add('playback resume')
        
        # Youtube video search condition, for instance 'watch youtube Metallica', 
        # 'show video Liverpool Manchester City' 
        elif self.second_part_command(cmd) and \
            (
            cmd.find('youtube') != -1 or \
            cmd.find('video') != -1 or \
            cmd.find('видео') != -1 or \
            cmd.find('ютюб') != -1
            ):
            for c in self.show_commands:
                if cmd.find(c) != -1:
                    cmd = cmd[cmd.find(cmd):]
                    cmd = cmd.replace(c, '')
            self.cmd['youtube'].add(f'video search {cmd}')

        elif cmd.find('gestures') != -1 and \
             cmd.find('recognition') != -1 and \
             cmd.find('mode') != -1:
            self.cmd['gesturesMode'] = True

        elif cmd.find('gestures') != -1 and \
             cmd.find('recognition') != -1 and \
             cmd.find('mode') != -1 and \
             cmd.find('off') != -1:
            self.cmd['gesturesMode'] = False

        if len(self.cmd) > 0:
            self.logger.debug(f'The following phrases have been detected: {self.cmd}')
        return cmd
    
    def second_part_command(self, cmd):
        """ Method checks if there is a word in the voice command associated with showing or
            concealing a widget.
            Returns True if there is a word associated with showing a widget.
            Returns False if there is a word associated with concealing a widget.
            Otherwise, returns None."""
        for c in self.hide_commands:
            if cmd.find(c) != -1:
                return False
        for c in self.show_commands:
            if cmd.find(c) != -1:
                return True
        return None        

if __name__ == '__main__':
    assistant = VoiceAssistant()
    assistant.assistant()
