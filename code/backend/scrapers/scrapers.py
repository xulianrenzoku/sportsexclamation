############################################################
# NOTE THAT THIS FILE WAS RUN ONCE TO GATHER HISTORICAL DATA
############################################################

import pandas as pd
import numpy as np
import time
import re
import requests
from selenium import webdriver
import os
from selenium.webdriver.common.keys import Keys

from sites_for_scraping import *

# regex for parsing the statistics column
value_regex = re.compile(r'\d+-?\d*')
column_regex = re.compile(r'[a-z]+')


#########################################
# Utility Functions for files on EC2 & S3
#########################################

def push(target_file, target_dest):
    """Push a file from the EC2 to S3"""
    os.system('aws s3 cp ' + target_file + ' s3://sportsextreme/' +
              target_dest + target_file)


def remove_local(target_file):
    """Delete a file on the EC2"""
    os.system('rm ' + target_file)


####################
# Scraping Functions
####################
def is_player(position):
    """A helper function used to assist in parsing
    the roto_guru tables to validate the data"""
    try:
        # testing if the posiiton value is PG or PG/SG
        return len(position) < 6

    # deals with when the position is NaN
    except TypeError:
        return False


def stat_flatten(row):
    """Parse the statistics column into different rows"""
    try:
        stats = row['stats'].split()
    except AttributeError:
        return

    for stat in stats:
        val = value_regex.findall(stat)[0]
        col = column_regex.findall(stat)[0]

        if col == 'pt':
            row['points'] = val
        elif col == 'rb':
            row['rebounds'] = val
        elif col == 'as':
            row['assists'] = val
        elif col == 'to':
            row['turnovers'] = val
        elif col == 'trey':
            row['threes'] = val
        elif col == 'st':
            row['steals'] = val
        elif col == 'bl':
            row['blocks'] = val
        elif col == 'fg':
            row['fg_attempts'] = val.split('-')[1]
            row['fg_made'] = val.split('-')[0]
        elif col == 'ft':
            row['ft_attempts'] = val.split('-')[1]
            row['ft_made'] = val.split('-')[0]
    return row


def roto_guru_scraper(service, month, day, year, file_dest):
    """Accesses the data table from SERVICE, with statistics
    from MONTH-DAY-YEAR and saves to FILE_DEST
    SERVICE will be fd for FanDuel and dk for DraftKings"""

    url = 'http://rotoguru1.com/cgi-bin/hyday.pl' + \
          f'?game={service}&mon={month}&day={day}&year={year}'

    html = requests.get(url).content
    df_list = pd.read_html(html)
    df = df_list[-2]

    df.columns = ('position player points salary team opponent ' +
                  'score minutes stats').split()

    # ensure that the rows are only player observations
    df = df[df['position'].apply(is_player)]
    # flatten the statistics column
    df = df.apply(lambda row: stat_flatten(row), axis=1)

    df.to_csv(file_dest, index=False)
    push(file_dest, '')


def roto_guru_helper(dest_folder):
    """Iterates over all days of basketball and saves values"""
    for service in 'fd dk'.split():
        for year in [2019]:
            for mon in [4]:
                for day in [7, 8, 9, 10]:
                    file_dest = dest_folder + \
                                f'{service}/{year}/{mon}-{day}.csv'
                    try:
                        roto_guru_scraper(service, mon, day, year, file_dest)
                    except ValueError:
                        print(f'Invalid date request: {file_dest}')


def rotoworld_injury_scraper(file_dest):
    """Scrape the RotoWorld injury report and save
    the results to FILE_DEST"""

    driver = webdriver.Chrome()
    # if doesn't work, take a look at adding path
    driver.get(rotoworld_injury_url)
    html = driver.find_element_by_tag_name('html').get_attribute('innerHTML')
    driver.quit()

    df_lst = pd.read_html(html)
    df = pd.concat(df_lst)
    df.reset_index(inplace=True)
    df.drop('index', axis=1, inplace=True)
    df.to_csv(file_dest, index=False)
    # chrome_options.add_argument('--headless')


class rotoworld_projection_scraper():
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.url_stats = 'https://rotogrinders.com/' + \
                         'projected-stats/nba-player?site='  # yahoo
        self.url_signin = 'https://rotogrinders.com/sign-in'

    def login(self):
        self.driver.get(self.url_stats + 'yahoo')

        self.driver.get(self.url_signin)

        text_area = self.driver.find_element_by_id('username')

        for key in 'manly_the_stanly':
            text_area.send_keys(key)
            time.sleep(np.random.uniform(0.1, 0.5))

        text_area.send_keys('\tjonrosspresta')
        text_area.send_keys(Keys.RETURN)

    def scrape(self, site, file_dest):
        self.driver.get(self.url_stats + site)

        time.sleep(1)

        html = self.driver.find_element_by_tag_name('html')\
            .get_attribute('innerHTML')

        with open(file_dest, 'w') as f:
            f.write(html)

        # input('Press enter to quit')


if __name__ == '__main__':
    yo = rotoworld_projection_scraper()
    yo.login()
    time.sleep(1)
    yo.scrape('yahoo', '/tmp/yahoo.html')
