#! python3
# parserbot.py - the module is used to obtain some data from Yandex.

import logging
import time
import requests
import bs4
import re
import datetime

class TeamBot:
    
    def __init__(self):
        self.logger = logging.getLogger('Gesell.teambot.TeamBot')
        self.url_calendar = 'https://www.sports.ru/spartak/calendar/'
        self.url_news = 'https://www.sports.ru/spartak/'
        self.url_coeffs_rpl = 'https://www.marathonbet.ru/su/popular/Football/Russia/Premier+League'
        self.url_coeffs_cl = 'https://www.marathonbet.ru/su/popular/Football/Clubs.+International/UEFA+Champions+League'
        self.url_coeffs_el = 'https://www.marathonbet.ru/su/popular/Football/Clubs.+International/UEFA+Europa+League'
        self.url_coeffs_popular = 'https://www.marathonbet.ru/su/popular/Football'
        self.rates_string = ''
        self.url_coeffs = 'https://www.marathonbet.ru/su/popular/Football'
        self.competitions = {'ремьер': 'РПЛ', 'чемпион': 'ЛЧ', 'овар': 'Товарищеская игра', 'упер': 'Суперкубок', 'вроп': 'ЛЕ', 'убок': 'Кубок России'}
        self.dateRegex = re.compile(r'\d\d.\d\d.\d\d\d\d') # Regex object for seeking dates.
        self.timeRegex = re.compile(r'\d\d:\d\d') # Regex object for seeking times.
        self.months = {'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4, 'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8, 'сентября': 9, 'октября': 10,
                       'ноября': 11, 'декабря': 12}
        self.logger.debug('An instance of TeamBot has been created.')
        
    def get_page(self, link):
        """ Loads a web page using 'requests' module. Returns the result as text if the status is OK.
        Otherwise, returns False."""
        res = requests.get(link)
        try:
            res.raise_for_status()
            self.logger.debug('Page {0} has been successfully loaded.'.format(link))
            return res.text
        except Exception as error:
            self.logger.error('Cannot get the page {0}'.format(link))
            self.logger.error('The following error occured: {0}'.format(error))
            return False

    def upcoming_game(self, current_time):
        """ Uses 'sports.ru' to obtain the data regarding the upcoming game."""
        res = self.get_page(self.url_calendar)
        if res == False:
            return None, None
        soup = bs4.BeautifulSoup(res, features='html.parser')        
        games = soup.find_all('tr')
        if len(games) > 0:
            self.logger.debug('Sports.ru upcoming game: successfully found games on the page.')
        else:
            self.logger.debug('Sports.ru upcoming game: cannot find games on the page.')
            return None, None
        upcoming_games = {}
        for game in games:
            date = self.dateRegex.search(game.getText())
            try:
                game_date = datetime.datetime.strptime(date.group(), '%d.%m.%Y')
                if game_date < current_time:
                    continue
                else:
                    self.logger.debug('Found a candidate date for the upcoming date')
                    time = self.timeRegex.search(game.getText())
                    try:
                        game_time = time.group()
                    except AttributeError:
                        game_time = '19:00'
                    game_date_and_time = datetime.datetime.strptime(date.group() + game_time, '%d.%m.%Y%H:%M')
                    self.logger.debug('Found a candidate date and time {0} for an upcoming game'.format(game_date_and_time))
                    titles = game.find_all(self.has_attr_title_and_not_class)
                    for title in titles:
                        for key in self.competitions.keys():
                            if title.get('title').find(key) != -1:
                                competition = self.competitions[key]
                            else:
                                rival = title.get('title')
                    self.logger.debug('Found the tournament: {0}'.format(competition))
                    self.logger.debug('Found the rival team: {0}'.format(rival))
                    if game.getText().find('Дома') != -1:
                        pitch = 'Дома'
                    else:
                        pitch = 'В гостях'
                    self.logger.debug('Found the venue: {0}'.format(pitch))
                    upcoming_games[game_date_and_time] = [rival, pitch, competition]
                    self.logger.debug('Overall: {0}, {1}'.format(game_date_and_time, upcoming_games[game_date_and_time]))
            except AttributeError:
                continue
        if len(upcoming_games) == 0:
            self.logger.debug('Something went wrong, there is no data for the upcoming game')
            return None, None
        date, rival, venue, competition = min(upcoming_games), upcoming_games[min(upcoming_games)][0], upcoming_games[min(upcoming_games)][1], upcoming_games[min(upcoming_games)][2]
        upcoming_games.pop(min(upcoming_games), None)
        if len(upcoming_games) == 0:
            self.logger.debug('Something went wrong, there is no data for the second game.')
            return {'date': date, 'rival': rival, 'venue': venue, 'competition': competition}, None
        date2, rival2, venue2, competition2 = min(upcoming_games), upcoming_games[min(upcoming_games)][0], upcoming_games[min(upcoming_games)][1], upcoming_games[min(upcoming_games)][2]
        self.logger.debug('Found the very forthcoming game: {0}'.format({'date': date, 'rival': rival, 'venue': venue, 'competition': competition}))
        return {'date': date, 'rival': rival, 'venue': venue, 'competition': competition}, {'date': date2, 'rival': rival2, 'venue': venue2, 'competition': competition2}
    
    def has_attr_title_and_not_class(self, tag):
        return tag.has_attr('title') and not tag.has_attr('class')
    
    def coefficients(self, team1, team2, competition):
        """ Gets the name of two teams. Looks for coefficients of the game between team1 and team2.
        Returns the values of team1 win, draw and team2 win. If the coeffs cannot be obtained, returns None, None, None."""
        # Marathonbet's web site is used for getting the coeffs.
        if competition == 'РПЛ':
            url = self.url_coeffs_rpl
        elif competition == 'ЛЧ':
            url = self.url_coeffs_cl
        elif competition == 'ЛЕ':
            url = self.url_coeffs_el
        else:
            url = self.url_coeffs_popular
        res = self.get_page(url)
        if res == False:
            return None, None, None
        soupObj = bs4.BeautifulSoup(res, features='html.parser')
        games = soupObj.find_all('div', class_='bg coupon-row')
        # The following title is used for looking for the game.
        for game in games:
            try:
                between = game['data-event-name']
                if between.find(team1) != -1 and between.find(team2) != -1:
                    found_game = game
                    logging.debug('The game has been found on the betting website')
                    break
            except Exception:
                continue
        else:
            logging.error('The game is not found on the betting website!')
            return None, None, None
        coeffs = found_game.find_all('span')
        # The coefficients for the game are floating numbers. The very first number in the table is irrelevant.
        counter = 4
        list_of_coeffs = []
        if len(coeffs) > 3:
            for coeff in coeffs:
                try:
                    float(coeff.getText())
                    list_of_coeffs.append(round(float(coeff.getText()), 1))
                    counter -= 1
                    if counter == 0:
                        logging.info('The coefficients for the upcoming game have been loaded.')
                        return list_of_coeffs[1], list_of_coeffs[2], list_of_coeffs[3]
                except ValueError:
                    continue
            else:
                logging.debug('Cannot find the coeffs on the betting website')
                return None, None, None
        else:
            logging.error('The coefficients have not been found')
            return None, None, None

if __name__ == '__main__':
    a = TeamBot()
    current_time = datetime.datetime.now()
    print(a.upcoming_game(current_time))


__version__ = '0.01' # 20.11.2019    
