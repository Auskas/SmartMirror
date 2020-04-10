#!/usr/bin/python3
# main.py - the main module for my smart mirror project.

import sys
from tkinter import *
import threading
import logging
from database import DatabaseBot
from teambot import TeamBot
from clockwidget import Clock
from spartakwidget import Spartak
from stockswidget import Stocks
from parserbot import ParserBot
from nextgame import NextGame
from livescore import LiveScore
from marquee import Marquee
from weatherwidget import Weather
#from face_recognition import FaceRecognizer
from hello import Hello
from message_widget import MessageWidget
from youtuber import Youtuber
#from gestures import Gestures
from gestures_recognizer import GesturesRecognizer
from wave_widget import WaveWidget
from voice_assistant import VoiceAssistant
from volume_widget import Volume
from covid import Covid


logger = logging.getLogger('Gesell')
logger.setLevel(logging.DEBUG)

logFileHandler = logging.FileHandler('gesell.log')
logFileHandler.setLevel(logging.DEBUG)

logConsole = logging.StreamHandler()
logConsole.setLevel(logging.DEBUG)

formatterFile = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
formatterConsole = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
logFileHandler.setFormatter(formatterFile)
logConsole.setFormatter(formatterConsole)

logger.addHandler(logFileHandler)
logger.addHandler(logConsole)

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logger.info('########## SCRIPT STARTED ##########')

if __name__ == '__main__':
    try:
        voiceAssistant = VoiceAssistant()

        databaseBot = DatabaseBot()

        parserBot = ParserBot()

        yandexThread = threading.Thread(target=parserBot.bot) # Thread 2. Updates stock rates.
        #yandexThread.daemon = True
        yandexThread.start()

        teamBot = TeamBot()

        nextgameBot = NextGame(databaseBot, teamBot)
        nextgameThread = threading.Thread(target=nextgameBot.upcoming_game) # Thread 3. Updates next game data.
        #nextgameThread.daemon = True
        nextgameThread.start()

        liveScore = LiveScore(databaseBot)
        scoreThread = threading.Thread(target=liveScore.score_notifier) # Thread 4. Updates live score.
        #scoreThread.daemon = True
        scoreThread.start()

        newsruThread = threading.Thread(target=parserBot.newsbot) # Thread 5. Updates the news.
        #newsruThread.daemon = True
        newsruThread.start()

        gesturesAssistant = GesturesRecognizer()
        if gesturesAssistant.camera_found:
            gesturesThread = threading.Thread(target=gesturesAssistant.tracker) # Thread 7. Recognizes gestures for controlling the mirror.
            #gesturesThread.daemon = True
            gesturesThread.start()

        window = Tk()
        window.title('Main Window')
        window.configure(bg='black')
        # Disables closing the window by standard means, such as ALT+F4 etc.
        #window.overrideredirect(True)
        w, h = window.winfo_screenwidth(), window.winfo_screenheight()
        window.geometry("%dx%d+0+0" % (w, h))
        logger.debug('Main window has been created')

        clock = Clock(window, databaseBot, voiceAssistant, gesturesAssistant)

        weather = Weather(window, voiceAssistant, gesturesAssistant)

        marquee = Marquee(window, parserBot, voiceAssistant, gesturesAssistant)

        spartak = Spartak(window, nextgameBot, databaseBot, liveScore, voiceAssistant, gesturesAssistant)

        stocks = Stocks(window, parserBot, voiceAssistant, gesturesAssistant)

        messageWidget = MessageWidget(window, voiceAssistant, gesturesAssistant)

        waveWidget = WaveWidget(window)

        volumeWidget = Volume(window)

        youtubeWidget = Youtuber(window, gesturesAssistant, voiceAssistant, waveWidget, volumeWidget) # Thread 8. The thread is used to control Youtube widget.
        youtubeThread = threading.Thread(target=youtubeWidget.status)
        #youtubeThread.daemon = True
        youtubeThread.start()

        covidWidget = Covid(window, parserBot, gesturesAssistant)
        covidThread = threading.Thread(target=parserBot.covidbot)
        covidThread.start()

        window.mainloop()

    except KeyboardInterrupt:
        sys.exit()

