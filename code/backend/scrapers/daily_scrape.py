import pandas as pd
import datetime
import re
import requests
import os

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
    """Parse the disorganized
    statistics column into different rows"""
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

    df.to_csv('/home/ec2-user/testing.csv')
    df.to_csv(file_dest, index=False)

    s3_path = f'{service}/{year}/{month}-{day}.csv'

    push(file_dest, s3_path)
    remove_local(file_dest)


def roto_guru_helper():
    """Helper function designed to be run once at 10PM
    every day to get the stats from the previous day"""
    today = datetime.datetime.today()
    # day adjustment because Linux is on UTC
    day, month, year = today.day-1, today.month, today.year

    roto_guru_scraper('dk', month, day, year,
                      'product-analytics-group-project-sportsexclamation/' +
                      f'code/backend/scrapers/dk/{year}/{month}-{day}.csv')

    roto_guru_scraper('fd', month, day, year,
                      'product-analytics-group-project-sportsexclamation/'
                      f'code/backend/scrapers/fd/{year}/{month}-{day}.csv')

    print('Succesful Scrape')


if __name__ == '__main__':
    roto_guru_helper()
