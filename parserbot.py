#! python3
# parserbot.py - the module is used to obtain some data from Yandex.

import logging
import time
import requests
import bs4

class ParserBot:
    
    def __init__(self):
        self.logger = logging.getLogger('Gesell.yandexbot.ParserBot')
        if __name__ == '__main__': # Creates a logger if the module is called directly.
            ch = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.setLevel(logging.DEBUG)
            self.logger.addHandler(ch)
        self.url = 'https://yandex.ru/'
        self.url_calendar = 'https://www.sports.ru/spartak/calendar/'
        self.url_marquee_news = 'https://www.newsru.com'
        self.url_astro = 'https://www.go-astronomy.com/solar-system/event-calendar.htm'
        self.url_covid = 'https://www.worldometers.info/coronavirus/'
        self.logger.debug('An instance of ParserBot has been created.')
        self.news = []
        self.rates_string = ''
        self.covid_figures = []

    def get_page(self, link):
        """ Loads a web page using 'requests' module. Returns the result as text if the status is OK.
        Otherwise, returns False."""
        try:
            res = requests.get(link)
        except Exception as error:
            self.logger.error(f'Cannot load the page, the following error occured: {error}')
            return False
        try:
            res.raise_for_status()
            self.logger.debug('Page {0} has been successfully loaded.'.format(link))
            return res.text
        except Exception as error:
            self.logger.error('Cannot get the page {0}'.format(link))
            self.logger.error('The following error occured: {0}'.format(error))
            return False
    
    def astro(self):
        """ Uses www.go-astronomy.com to obtain the data regarding today's astronomical events."""
        res = self.get_page(self.url_astro)
        if res == False:
            return None
        soup = bs4.BeautifulSoup(res, features='lxml')
        candidates = soup.find_all('p')
        for candidate in candidates:
            print(candidate.getText())
            print('#################')

    def rates(self):
        """ Uses 'yandex.ru' to obtain stocks data."""
        print('Trying to get stocks rates...')
        values = []
        changes = []
        res = self.get_page(self.url)
        if res == False:
            return None
        soup = bs4.BeautifulSoup(res, features='html.parser')        
        rates = soup.find_all('span', class_='inline-stocks__value_inner')
        if len(rates) < 3:
            self.logger.error('Cannot find the rates on the page.')
            self.rates_string = ''
        for rate in rates:
            values.append(rate.getText())
        directions = soup.find_all('div', class_='a11y-hidden inline-stocks__cell_type_delta-label')
        if len(directions) < 3:
            self.logger.error('Cannot find the rates delta on the page.')
            return None
        for direction in directions:
            if direction.getText()[0] == '+':
                changes.append('↑')
            elif direction.getText()[0] == '-':
                changes.append('↓')
            else:
                changes.append('')
        self.rates_string = f'$ {values[0]}{changes[0]}   € {values[1]}{changes[1]}   Brent {values[2]}{changes[2]}'
        self.logger.debug('Got the string for current exchange rates.')

    def marquee_news(self):
        """ Downloads the webpage http://newsru.com. 
        Finds the main news on the page.
        Also finds other news on the page."""
        new_news = []
        res = self.get_page(self.url_marquee_news)
        if res == False:
            return None
        soup = bs4.BeautifulSoup(res, features='html.parser')
        mainNewsTitle = soup.find('div', class_='sp-main-title')
        mainNewsText = soup.find('div', class_='sp-main-text')
        new_news.append('. '.join([mainNewsTitle.getText().strip(), mainNewsText.getText().strip()]) + '   ***   ')
        newsTags = soup.find_all('div', class_='left-feed-text')
        number_of_news = 1
        for tag in newsTags:
            tagTitle = tag.find('div', class_ = 'left-feed-title')
            tagText = tag.find('div', class_= 'left-feed-anons')
            new_news.append(tagTitle.getText().strip() + '   ***   ')
            number_of_news += 1
            if number_of_news == 10:
                break
        if len(new_news) > 0:
            self.news = new_news[:]

    def covid(self):
        res = self.get_page(self.url_covid)
        if res == False:
            return None
        self.covid_figures = []
        soup = bs4.BeautifulSoup(res, features='html.parser')
        figures = soup.find_all('div', class_='maincounter-number')
        for figure in figures:
            self.covid_figures.append(figure.getText())
        national_figures = soup.find_all('tr')
        for nation in national_figures:
            country = nation.getText()
            if country.find('Russia') != -1:
                #print(nation.getText().split())
                self.covid_figures.extend(country.split()[1:6])
                break

    def bot(self):
        while True:
            self.rates()
            if self.rates_string == '':
                time.sleep(60)
            else:
                time.sleep(3600)

    def newsbot(self):
        while True:
            self.marquee_news()
            if len(self.news) == 0:
                time.sleep(60)
            else:
                time.sleep(3600)

    def covidbot(self):
        while True:
            self.covid()
            if len(self.covid_figures) < 8:
                time.sleep(3600)
            else:
                time.sleep(43200)

if __name__ == '__main__':
    a = ParserBot()
    a.covid()
    print(a.covid_figures)

__version__ = '0.01' # 20.11.2019    
