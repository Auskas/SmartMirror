#! python3
# nextgame.py - the module updates the upcoming game data.

import logging
import datetime, time

class NextGame:

    def __init__(self, databasebot, teambot):
        self.logger = logging.getLogger('Gesell.nextgame.NextGame')
        self.logger.info('Initializing an instance of NextGameBot...')
        self.databaseBot = databasebot
        self.teamBot = teambot
        self.nextgame_string = ''

    def upcoming_game(self):
        if self.databaseBot.teamDatabase['upcoming_game']['date'] != '20.10.2019':
            gamedata = self.databaseBot.teamDatabase['upcoming_game']
            competition = gamedata['competition']
            rival = gamedata['rival']
            venue = gamedata['venue']
            if venue == 'Дома':
                team1, team2 = 'Спартак', rival
            elif venue == 'В гостях':
                team1, team2 = rival, 'Спартак'
            date = gamedata['date'] + ' ' + gamedata['time']
            if gamedata['coeffs'][0] != 'None':
                coeffs_string = '  '.join([str(gamedata['coeffs'][0]), str(gamedata['coeffs'][1]), str(gamedata['coeffs'][2])])
            else:
                coeffs_string = ''
            self.nextgame_string = f'{competition}   {team1} - {team2}   {date}   Кэфы: {coeffs_string}'
        while True:
            current_time = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
            upcoming_game_time = self.databaseBot.get_upcoming_game_time()
            # If current time is less than the upcoming game time in the database by at least one hour.
            if current_time + datetime.timedelta(hours=1) < upcoming_game_time:
                time.sleep(3600) # Sleeps for one hour.
                continue
            # Less than one hour prior to the game.
            elif current_time < upcoming_game_time:
                time.sleep(60) # Sleeps for one minute.
                continue
            # The game has just begun - the cycle waits till the game ends.
            elif (upcoming_game_time + datetime.timedelta(hours=4) > current_time >= upcoming_game_time
                    and self.databaseBot.teamDatabase['upcoming_game']['date'] != '20.10.2019'):
                game_started = False
                while True:
                    # When it is the time but the game has not started yet, simply waits till the beginning of the game.
                    if self.databaseBot.teamDatabase['current_game'] == 'None' and game_started == False:
                        time.sleep(60)
                        continue
                    # When the game starts, changes the flag game_started to True.
                    elif self.databaseBot.teamDatabase['current_game'] != 'None' and game_started == False:
                        game_started = True
                        time.sleep(60)
                        continue
                    # When the game ends, updates the next games data, breaks the inner cycle.
                    elif self.databaseBot.teamDatabase['current_game'] == 'None' and game_started:
                        time.sleep(30)
                        self.logger.info('Next game updater: The game has just ended, it is the right time to update the next games data.')
                        next_game, next_next_game = self.teamBot.upcoming_game(current_time)
                        break
                    # Waiting till the game ending.
                    else:
                        time.sleep(300)
                        self.logger.debug('Next game updater: Waiting till the game ends.')
            # There is no data in the database regarding the upcoming game. In fact, there is a default date 20.10.2019.
            # Or the script is restarted and the upcoming game had not been uploaded prior to the restarting.
            else:
                next_game, next_next_game = self.teamBot.upcoming_game(current_time)
            # There is no data about the next game.
            if next_game == None:
                self.logger.critical('Could not obtain the data about the next game')
            else:
                self.databaseBot.add_upcoming_game(next_game)
                self.logger.debug('The upcoming game data has been just updated.')
                upcoming_game = self.databaseBot.teamDatabase['upcoming_game']
                rival = upcoming_game['rival']
                venue = upcoming_game['venue']
                competition = upcoming_game['competition']
                date = upcoming_game['date']
                if venue == 'Дома':
                    team1, team2 = 'Спартак', rival
                elif venue == 'В гостях':
                    team1, team2 = rival, 'Спартак'
                coeffs = self.teamBot.coefficients(team1, team2, competition)
                # If the coeffs aren't available.
                if coeffs[0] != None and coeffs[1] != None and coeffs[2] != None:
                    self.logger.debug('The coefficients for the upcoming game have been updated')
                    self.databaseBot.change_coeffs(coeffs)
                    coeffs_string = '  '.join([str(coeffs[0]), str(coeffs[1]), str(coeffs[2])])
                else:
                    self.logger.error('Cannot find the coeffs for the upcoming game.')
                    coeffs_string = ''
                self.nextgame_string = f'{competition}   {team1} - {team2}   {date}   Кэфы: {coeffs_string}'
            # There is no data about the game after the next game.
            if next_next_game == None:
                self.logger.critical('Could not obtain the data about the game after the upcoming game')
            else:
                self.databaseBot.add_after_upcoming_game(next_next_game)
                self.logger.debug('The game after the upcoming game data has been just updated.')
                after_upcoming_game = self.databaseBot.teamDatabase['after_upcoming_game']
                rival = after_upcoming_game['rival']
                venue = after_upcoming_game['venue']
                competition = after_upcoming_game['competition']
                if venue == 'Дома':
                    team1, team2 = 'Спартак', rival
                elif venue == 'В гостях':
                    team1, team2 = rival, 'Спартак'
                coeffs = self.teamBot.coefficients(team1, team2, competition)
                # If the coeffs aren't available.
                if coeffs[0] != None and coeffs[1] != None and coeffs[2] != None:
                    self.logger.debug('The coefficients for the game after the upcoming game have been updated')
                    self.databaseBot.change_coeffs_2(coeffs)
                else:
                    self.logger.error('Cannot find the coeffs for the game after the next game.')
            self.databaseBot.save()
            time.sleep(86400)
