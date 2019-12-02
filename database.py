#! python3
# database.py - contains classes for database bots.

import json
import logging
import datetime

class DatabaseBot:
    def __init__(self):
        self.logger = logging.getLogger('Gesell.database.DatabaseBot')
        self.logger.info('Initializing an instance of DatabaseBot...')
        try:
            with open('team.txt') as teamDatabaseFile:
                teamDatabaseData = teamDatabaseFile.read()
                self.teamDatabase = json.loads(teamDatabaseData)
            self.logger.info('The team\'s database has been opened.')
        except Exception as errorTeam:
            self.teamDatabase = {'news': {'last_newsletter': {'date': '20.10.2019', 'topic': '', 'link': ''}},
                                 'last_game': {'date': '20.10.2019', 'time': '18:00', 'rival': 'None', 'venue': 'None', 'competition': 'None',
                                               'goalsHomeTeam': '0', 'goalsAwayTeam': '0'},
                                 'current_game': 'None',
                                 'upcoming_game': {'date': '20.10.2019', 'time': '18:00', 'rival': 'None', 'venue': 'None', 'competition': 'None',
                                                   'coeffs': ['None', 'None', 'None'], 'stats': {'h2h': 'None'}},
                                 'after_upcoming_game': {'date': '20.10.2019', 'time': '18:00', 'rival': 'None', 'venue': 'None', 'competition': 'None',
                                                   'coeffs': ['None', 'None', 'None'], 'stats': {'h2h': 'None'}}}
            self.logger.error('Cannot get data from teams\' database file. Error: {0}'.format(errorTeam))
        try:
            with open('users.txt') as usersDatabaseFile:
                usersDatabaseData = usersDatabaseFile.read()
                self.usersDatabase = json.loads(usersDatabaseData)
            self.logger.info('Users\' database has been loaded.')
        except Exception as errorUsers:
            self.usersDatabase = {'Dmitry': {'night': False, 'morning': False, 'day': False, 'evening': False},
                                  'Anna': {'night': False, 'morning': False, 'day': False, 'evening': False},
                                  'Yaroslav': {'night': False, 'morning': False, 'day': False, 'evening': False},
                                  'Agniya': {'night': False, 'morning': False, 'day': False, 'evening': False}}
            self.logger.error('Cannot get data from users\' database file. Error: {0}'.format(errorUsers))

    def get_upcoming_game_time(self):
        return datetime.datetime.strptime(self.teamDatabase['upcoming_game']['date'] + self.teamDatabase['upcoming_game']['time'], '%d.%m.%Y%H:%M')

    def save(self):
        teamDatabaseFile = open('team.txt', 'w')
        json.dump(self.teamDatabase, teamDatabaseFile)
        teamDatabaseFile.close()
        usersDatabaseFile = open('users.txt', 'w')
        json.dump(self.usersDatabase, usersDatabaseFile)
        usersDatabaseFile.close()

    def change_coeffs(self, coeffs):
        self.teamDatabase['upcoming_game']['coeffs'] = coeffs

    def change_coeffs_2(self, coeffs):
        self.teamDatabase['after_upcoming_game']['coeffs'] = coeffs        

    def add_upcoming_game(self, upcoming_game_data):
        self.teamDatabase['upcoming_game']['date'] = upcoming_game_data['date'].strftime('%d.%m.%Y')
        self.teamDatabase['upcoming_game']['time'] = upcoming_game_data['date'].strftime('%H:%M')
        self.teamDatabase['upcoming_game']['rival'] = upcoming_game_data['rival']
        self.teamDatabase['upcoming_game']['venue'] = upcoming_game_data['venue']
        self.teamDatabase['upcoming_game']['competition'] = upcoming_game_data['competition']
        self.upcoming_game_time = datetime.datetime.strptime(self.teamDatabase['upcoming_game']['date'] + self.teamDatabase['upcoming_game']['time'], '%d.%m.%Y%H:%M')
        self.teamDatabase['upcoming_game']['coeffs'] = ['None', 'None', 'None']

    def add_after_upcoming_game(self, upcoming_game_data):
        self.teamDatabase['after_upcoming_game']['date'] = upcoming_game_data['date'].strftime('%d.%m.%Y')
        self.teamDatabase['after_upcoming_game']['time'] = upcoming_game_data['date'].strftime('%H:%M')
        self.teamDatabase['after_upcoming_game']['rival'] = upcoming_game_data['rival']
        self.teamDatabase['after_upcoming_game']['venue'] = upcoming_game_data['venue']
        self.teamDatabase['after_upcoming_game']['competition'] = upcoming_game_data['competition']
        self.after_upcoming_game_time = datetime.datetime.strptime(self.teamDatabase['after_upcoming_game']['date'] + self.teamDatabase['after_upcoming_game']['time'], '%d.%m.%Y%H:%M')
        self.teamDatabase['after_upcoming_game']['coeffs'] = ['None', 'None', 'None']


__version__ = '0.01' # 20.11.2019

