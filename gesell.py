#! python3
# gesell.py - main module for my smart mirror project.

import os
import sys
print(os.getcwd())
from tkinter import *
import datetime
import time
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
from face_recognition import FaceRecognizer
import threading
from hello import Hello
from message_widget import MessageWidget
from youtuber import Youtuber
from voice_assistant import VoiceAssistant


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
        databaseBot = DatabaseBot()
        parserBot = ParserBot()
        yandexThread = threading.Thread(target=parserBot.bot) # Thread 2. Updates stock rates.
        yandexThread.start()
        teamBot = TeamBot()
        nextgameBot = NextGame(databaseBot, teamBot)
        nextgameThread = threading.Thread(target=nextgameBot.upcoming_game) # Thread 3. Updates next game data.
        nextgameThread.start()
        liveScore = LiveScore(databaseBot)
        scoreThread = threading.Thread(target=liveScore.score_notifier) # Thread 4. Updates live score.
        scoreThread.start()
        newsruThread = threading.Thread(target=parserBot.newsbot) # Thread 5. Updates the news.
        newsruThread.start()
        #faceRecognizer = FaceRecognizer()
        #faceRecognizerThread = threading.Thread(target=faceRecognizer.realtime_recognizer) # Thread 6. Updates the list of detected users.
        #faceRecognizerThread.start()
        faceRecognizer = None
        assistant = VoiceAssistant()
        assistantThread = threading.Thread(target=assistant.assistant)
        assistantThread.start()
        window = Tk()
        window.title('Main Window')
        window.configure(bg='black')
        window.overrideredirect(True)
        w, h = window.winfo_screenwidth(), window.winfo_screenheight()
        window.geometry("%dx%d+0+0" % (w, h))
        logger.debug('Main window has been created')
        clock = Clock(window, databaseBot)
        #hello = Hello(window, faceRecognizer, clock, databaseBot)
        #weather = Weather(window)
        marquee = Marquee(window, parserBot)
        spartak = Spartak(window, nextgameBot, databaseBot, liveScore)
        stocks = Stocks(window, parserBot)
        #messageWidget = MessageWidget(window, clock, databaseBot)
        youtubeWidget = Youtuber(window, assistant)
        window.mainloop()
    except KeyboardInterrupt:
        sys.exit()

