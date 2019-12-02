#! python3
# livescore.py - score notifier for my Smart Mirror project.

import logging, datetime, time

class LiveScore:

    def __init__(self, databasebot):
        self.logger = logging.getLogger('Gesell.score.Notifier')
        self.logger.info('Initializing an instance of ScoreNotifierBot')
        self.url_live = "https://api-football-v1.p.rapidapi.com/v2/fixtures/live/"
        self.url_result = "https://api-football-v1.p.rapidapi.com/v2/fixtures/id/"
        self.headers = {'x-rapidapi-host': "api-football-v1.p.rapidapi.com", 'x-rapidapi-key': "d8c0650107msh070c115e4509599p15dfe9jsn9b64939b57cf"}
        self.databaseBot = databasebot
        self.status = '' # Used to determine the phase of a match: First Half, Half Time, Second Half.
        self.goal = False # Used to check if there is a fresh goal scoared.
        self.livescore = '0 - 0'
        self.elapsed = '0'

    def score_notifier(self):
        """ Notifies the subscribed users about scored goals in a game."""
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # !!! Add extra time and penalty notifications !!!
        while True:
            upcoming_game_time = self.databaseBot.get_upcoming_game_time()
            if upcoming_game_time == datetime.datetime(2019,10,20): # the next game has not been loaded yet.
                self.logger.debug('Cannot find the upcoming game data. Sleeping for 30 seconds...')
                time.sleep(30)
                continue
            current_time = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
            # If there are 24 hours of more prior to the game, sleeps for 24 hours.
            if current_time + datetime.timedelta(hours=24) < upcoming_game_time:
                self.logger.debug('More than 24 hours prior to the game. Sleeping for 24 hours...')
                time.sleep(86400)
                continue
            # If there are 24 hours or less prior to the game (or the game has alredy begun in case of console restart), sleeps till the beginning of the game.
            elif current_time + datetime.timedelta(hours=24) >= upcoming_game_time and current_time < upcoming_game_time + datetime.timedelta(hours=4):
                rest_time_seconds = (upcoming_game_time - current_time).seconds
                if current_time < upcoming_game_time:
                    rest_time_seconds = (upcoming_game_time - current_time).seconds + 60
                    self.logger.debug('Less than 24 hours prior to the game. Sleeping for {0} seconds till the 60th second after the beginning of the game...'.format(rest_time_seconds))
                else:
                    self.logger.debug('The game has already started')
                    rest_time_seconds = 0
                time.sleep(rest_time_seconds)
                rival = self.databaseBot.teamDatabase['upcoming_game']['rival']
                date = self.databaseBot.teamDatabase['upcoming_game']['date']
                venue = self.databaseBot.teamDatabase['upcoming_game']['venue']
                score = ['0', '0']
                match_started = False
                if venue == 'Дома':
                    self.home_team1, self.away_team = 'Спартак', rival
                elif venue == 'В гостях':
                    self.home_team1, self.away_team = rival, 'Спартак'
                self.logger.info('The game between {0} and {1} should begin right now'.format(self.home_team, self.away_team))
                while True:
                    current_time = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
                    if current_time > upcoming_game_time + datetime.timedelta(hours=4):
                        self.logger.debug('Quitting from live update because the time has run out (+4 hours)')
                        self.status = ''
                        self.goal = False
                        self.livescore = '0 - 0'
                        self.elapsed = '0'
                        self.databaseBot.teamDatabase['current_game'] = 'None'
                        break
                    live = self.get_score()
                    if live == None and match_started == False:
                        self.logger.debug('Score notifier: the game should have been started, but there are no APIs. Sleeping for 3 minutes')
                        time.sleep(180)
                        continue
                    if live == None and match_started:
                        self.logger.debug('The game has ended because there are no live APIs')
                        score = self.get_final_results(fixture_id)
                        self.databaseBot.teamDatabase['current_game'] = 'None'
                        if (self.home_team == 'Спартак' and score[0] > score[1]) or (self.away_team == 'Спартак' and score[1] > score[0]):
                            winner = 'Спартак'
                            self.logger.info('The winner is Spartak!')
                        elif score[0] == score[1]:
                            winner = 'Ничья'
                            self.logger.info('The final result is the draw')
                        else:
                            winner = rival
                            self.logger.info('The winner is {0}'.format(rival))
                        self.logger.debug('Sleeping for 24 hours...')
                        self.status = ''
                        self.goal = False
                        self.livescore = '0 - 0'
                        self.elapsed = '0'
                        time.sleep(86400)
                        break
                    else:
                        if live == None:
                            self.logger.debug('The game should have been already started, but there are no APIs. Sleeping for 2 minutes..')
                            time.sleep(120)
                            continue
                        # A game has just begun.
                        if match_started == False:
                            self.status = 'Первый тайм'
                            fixture_id = live[7]
                            self.logger.debug('The game has just started, fixture_id {0}'.format(fixture_id))
                            # Notifies the users about the kick-off.
                            self.databaseBot.teamDatabase['current_game'] = {'homeTeam': self.home_team, 'awayTeam': self.away_team, 'goalsHomeTeam': '0', 'goalsAwayTeam': '0',
                                                                    'status': live[2]}
                            match_started = True
                        self.elapsed = live[8]  
                        # During the halftime there is a while cycle which ends when API status of the game changes from HT to 2H.
                        if live[2] == 'HT':
                            self.status = 'Перерыв'
                            self.databaseBot.teamDatabase['current_game'] = {'homeTeam': self.home_team, 'awayTeam': self.away_team, 'goalsHomeTeam': '0', 'goalsAwayTeam': '0',
                                                                    'status': live[2]}
                            self.logger.info('End of the first half.')
                            while live[2] == 'HT':
                                time.sleep(120)
                                live = self.get_score()
                                self.logger.debug('Half time is continuing....')
                            self.status = 'Второй тайм'
                            self.logger.info('Second half has just started.')
                            self.databaseBot.teamDatabase['current_game'] = {'homeTeam': self.home_team, 'awayTeam': self.away_team, 'goalsHomeTeam': '0', 'goalsAwayTeam': '0',
                                                                    'status': live[2]}
                        self.logger.debug('The game is continuing...')
                        if live[0] > score[0] or live[1] > score[1]: # if either of the teams scored (or both)
                            self.logger.debug('GOAL!!!')
                            self.goal = True
                            self.livescore = f'{live[0]} - {live[1]}'
                            if live[0] > score[0]:
                                self.databaseBot.teamDatabase['current_game']['goalsHomeTeam'] = live[0]
                            else:
                                self.databaseBot.teamDatabase['current_game']['goalsAwayTeam'] = live[1]
                            if (self.home_team == 'Спартак' and live[0] > score[0]) or (self.away_team == 'Спартак' and live[1] > score[1]):
                                self.logger.info('Spartak scored a goal: {0} - {1}'.format(live[0], live[1]))
                            if (self.home_team == 'Спартак' and live[1] > score[1]) or (self.away_team == 'Спартак' and live[0] > score[0]):
                                self.logger.info('{0} scored a goal: {1} - {2}'.format(rival, live[0], live[1]))
                            score = [live[0], live[1]]
                        elif live[0] < score[0] or live[1] < score[1]: # if the goal was canceled
                            self.goal = False
                            self.logger.info('Score notifier: the goal was canceled!')
                            if live[0] < score[0]:
                                self.databaseBot.teamDatabase['current_game']['goalsHomeTeam'] = live[0]
                            else:
                                self.databaseBot.teamDatabase['current_game']['goalsAwayTeam'] = live[1]
                            score = [live[0], live[1]]
                            self.livescore = f'{live[0]} - {live[1]}'
                        else:
                            self.goal = False
                        time.sleep(90) # updates the score every 90 seconds.

    def get_api(self, link):
        # Checks whether the link can be loaded.
        res = requests.get(link, headers=self.headers)
        try:
            res.raise_for_status()
            self.logger.debug('Got the response from API Football')
            return res.json()
        except Exception as error:
            self.logger.error('Cannot get the data from API Football')
            return False
        
    def get_score(self, competition):
        """ Returns a list of the following strings:
            goals scored by the home team,
            goals scored by the away team,
            status of the match (i.e. "Second Half")
            score after the first half (i.e. "1-0")
            score after the fulltime
            score after the extratime
            score after the penalties

            If the game is not started or finished,
            returns None."""
        if competition == 'РПЛ':
            url = self.url_live + '511'
        elif competition == 'ЛЧ':
            url = self.url_live + '530'
        elif competition == 'ЛЕ':
            url = self.url_live + '137'
        res = self.get_api(url)
        if res == False:
            return None
        matches = res['api']['fixtures']
        for i in range(len(matches)):
            if matches[i]['homeTeam']['team_name'] == 'Spartak Moscow':
                fixture_id = str(matches[i]['fixture_id'])
                match_id = i
                break
            elif matches[i]['awayTeam']['team_name'] == 'Spartak Moscow':
                fixture_id = str(matches[i]['fixture_id'])
                match_id = i
                break
        else:
            self.logger.debug('The game has not been found. Probably has not started yet or already finished.')
            return None
        goalsHomeTeam = str(matches[match_id]['goalsHomeTeam'])
        goalsAwayTeam = str(matches[match_id]['goalsAwayTeam'])
        status = matches[match_id]['statusShort']
        scoreHalftime = matches[match_id]['score']['halftime']
        scoreFulltime = matches[match_id]['score']['fulltime']
        scoreExtratime = matches[match_id]['score']['extratime']
        scorePenalty = matches[match_id]['score']['penalty']
        elapsed = str(matches[match_id]['elapsed'])
        return [goalsHomeTeam, goalsAwayTeam, status, scoreHalftime, scoreFulltime,
                scoreExtratime, scorePenalty, fixture_id, elapsed]

    def get_final_results(self, fixture_id):
        url = self.url_result + fixture_id
        res = self.get_api(url)
        if res == False:
            self.logger.error('Cannot get the final results')
            return None
        if res['api']['results'] == 0:
            return None
        results = res['api']['fixtures'][0]
        homeTeamName = results['homeTeam']['team_name']
        awayTeamName = results['awayTeam']['team_name']
        goalsHomeTeam = results['goalsHomeTeam']
        goalsAwayTeam = results['goalsAwayTeam']
        self.logger.info('Final result: {0} - {1} final score {2} - {3}'.format(homeTeamName, awayTeamName, goalsHomeTeam, goalsAwayTeam))
        return goalsHomeTeam, goalsAwayTeam

__version__ = '0.01' #20.11.2019
