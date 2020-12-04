# import librariers, check for exact classification

from _datetime import datetime as dt
from dateutil.parser import parse
from bs4 import BeautifulSoup
import pandas as pd
import unicodedata
import requests
import time
import csv

# create class mediumScraper
class mediumScraper:

    def __init__(self, keyword, file_name, start, finish):
        """
        Initialize class
        """
        self.keyword = keyword
        self.file_name = file_name
        self.start = dt.strptime(start,'%d-%m-%Y').date()
        self.finish = dt.strptime(finish,'%d-%m-%Y').date()

    def create_file(self):
        """
        Checks if a file with the provided filename already exists, if not, creates new file
        :param file_name: str
        :return: None
        """
        try:
            f = open(self.file_name)
            f.close()
        except IOError:
            csv_columns = ['date', 'title', 'text']
            with open(self.file_name, 'a', encoding='UTF-8', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_columns, delimiter='|')
                writer.writeheader()
                csvfile.close()

    def save_article(self, article):
        """
        Takes a DataFrame with the article information and appends it to the previously created csv file
        :param article: DataFrame
        :param csv_file: str
        :return: None
        """
        csv_columns = ['date', 'title', 'text']
        print('------------------')
        with open(self.file_name, 'a', encoding='UTF-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns, delimiter='|')
            writer.writerow(article)
            csvfile.close()

    def get_links(self, url):
        """
        Scrapes url for each link on the provided page and its publication date
        :param url: str
        :return: list of url
        """
        links = []
        data = requests.get(url)
        soup = BeautifulSoup(data.content, 'html.parser')
        articles = soup.findAll('div', {"class": ""})
        dates = soup.findAll('time')
        for i in range(0, len(articles)):
            link = {'link': articles[i].contents[0].attrs['href'],
                    'date': parse(dates[i].attrs['datetime']).date()}
            links.append(link)
        return links

    def get_articles(self, url):
        """
        Calls get_links and iterates through the list of urls and extracts article metadata and full text for the links in the desired time frame
        :param url: str
        :param csv_file: str
        :param start: str
        :param finish: str
        :return: None
        """
        links = self.get_links(url)
        links = [link for link in links if self.start <= link['date'] <= self.finish]
        for link in links:
            try:
                data = requests.get(link["link"])
                soup = BeautifulSoup(data.content, 'html.parser')
                try:
                    title = soup.findAll('title')[0].get_text()
                except IndexError:
                    title = 'No title'
                print(str(link['date']) + ': ' + title)
                paras = soup.findAll(['p', 'li'])
                text = ''
                for para in paras:
                    text += unicodedata.normalize('NFKD', para.get_text()) + ' '
                article = {'date': link['date'],
                           'title': title,
                           'text': text}
                self.save_article(article)
            except requests.exceptions.ConnectionError:
                pass
            time.sleep(0.2)

    def get_date(self, year, url, direction):
        """
        Finds first date or last date of the given year, sorts them by desceding order
        :param year: int
        :param url: str
        :param direction: int
        :return: date in str format
        """
        # year: the year to look in
        # url -> gets link to archive from availability()
        # direction -> 0: first/oldest article
        #              1: last/newest article
        date_list = []
        data = requests.get(url + '/' + str(year))
        soup = BeautifulSoup(data.content, 'html.parser')
        months = soup.findAll('div', {'class': 'timebucket u-inlineBlock u-width80'})
        month_list = self.navigator(months)
        if month_list == 0:
            pass
        else:
            if direction == 1:
                data = requests.get(month_list[-1].contents[0].attrs['href'])
                soup = BeautifulSoup(data.content, 'html.parser')
            else:
                data = requests.get(month_list[0].contents[0].attrs['href'])
                soup = BeautifulSoup(data.content, 'html.parser')
        for date in soup.findAll('time'):
            date_list.append(parse(date.attrs['datetime']).date())
        if direction == 1:
            return date_list[-1].strftime("%b %d, %Y")
        else:
            return date_list[0].strftime("%b %d, %Y")


    def availability(self):
        """
        Gets list of years that the keyword was found in. Additionally prints information about the first and latest
        articles posted in regards to the given keyword.
        :param keyword: str
        :return: list of int
        """
        url = 'https://medium.com/tag/%s/archive' % self.keyword
        data = requests.get(url)
        soup = BeautifulSoup(data.content, 'html.parser')
        years = soup.findAll('div', {'class': 'timebucket u-inlineBlock u-width50'})
        year_list = []
        for year in years:
            year_list.append(year.string)
        first = self.get_date(year_list[0], url, 0)
        last = self.get_date(year_list[-1], url, 1)
        print('First article: ' + first + '\n' + 'Last article : ' + last)
        return year_list


    def navigator(self, date_list):
        """
        Helper function for scrape(). Eliminates None values from list.
        :param date_list: list of dict
        :return: list of dict
        """
        list = []
        if len(date_list) == 0:
            return 0
        for date in date_list:
            if date.string is not None:
                list.append(date)
        return list


    def scrape(self, years):
        """
        Iterates through threefold process. First through years, second through months and lastly through days.
        Extracts all articles on any of the levels, if further level is empty.
        :param keyword: str
        :param file_name: str
        :param start: str
        :param finish: str
        :param years: list of int
        :return: Message that scraping is completed.
        """
        # initial scraping of /latest
        url = 'https://medium.com/tag/' + self.keyword + '/latest'
        self.get_articles(url)
        # search through archive
        years = [year for year in years if self.start.year <= int(year) <= self.finish.year]
        for year in years:
            try:
                url = 'https://medium.com/tag/%s' % self.keyword + '/archive/%s' % year
                data = requests.get(url)
                soup = BeautifulSoup(data.content, 'html.parser')
                months = soup.findAll('div', {'class': 'timebucket u-inlineBlock u-width80'})
                month_list = self.navigator(months)
                if month_list == 0:
                    self.get_articles(url)
                else:
                    for month in month_list:
                        data = requests.get(month.contents[0].attrs['href'])
                        soup = BeautifulSoup(data.content, 'html.parser')
                        days = soup.findAll('div', {'class': 'timebucket u-inlineBlock u-width35'})
                        day_list = self.navigator(days)
                        if day_list == 0:
                            self.get_articles(month.contents[0].attrs['href'])
                        else:
                            for day in day_list:
                                self.get_articles(day.contents[0].attrs['href'])
            except requests.exceptions.SSLError as error:
                print(error)
                print('--- short break ---')
                time.sleep(30)

        print('Scraping done')
        return 0


    def run(self):
        """
        Executes the functions defined in the class. Prints keyword for articles extracted. Removes duplicates in csv file.
        """
        # add .csv extention if not included in file_name
        if len(self.file_name.split('.')) == 1:
            self.file_name += '.csv'
        
        # print keyword
        print('Timespan for articles with the tag: "%s"' % self.keyword)

        # create file and run scraper
        years = self.availability()
        self.create_file()
        self.scrape(years)

        # remove duplicates
        print('Removing duplicates')
        df = pd.read_csv(self.file_name, self.file_name, delimiter='|')
        len1 = len(df)
        df = df.drop_duplicates(subset=['text'])
        len2 = len1 - len(df)
        df.to_csv(self.file_name, sep='|', index=False)
        print('Dropped %s duplicates' % str(len2))

