import boto3
import pandas as pd
import numpy as np
import pickle
import re

re_ = '(?<=[,])(?=[^\s])'


def load_file(target_file):
    """Retrieves the requested file from S3"""
    s3 = boto3.client('s3')
    data = s3.get_object(Bucket='sportsextreme', Key=target_file)
    contents = str(data['Body'].read())[2:-1]
    data = [re.split(re_, line)[:-1] for line in contents.split('\\n')][:-2]
    data = [[d[:-1] for d in d_] for d_ in data]
    df_data = pd.DataFrame(data=data[1:], columns=data[0])
    df_data['player'] = df_data['player'].apply(lambda x: x.strip('"'))
    return df_data


def make_team_hist(player_lst, service, df):
    """Given a list of player names and the service (fd/dk)
    this will sample from historical games for that player
    and create a distribution of the lineup's total points"""

    # Note his has been deprecated now that I wrote to pickle
    samples = []

    for player in player_lst:
        games = df[df['player'] == player]
        if service == 'fd':
            hist_points = games['fd_pt']
        else:
            assert(service == 'dk')
            hist_points = games['dk_pt']
        sample = hist_points.sample(100, replace=True).values
        samples.append(sample)

    samples = np.array(samples)
    totals = np.sum(samples, axis=0)
    return totals


def create_lineup_dist(player_lst):
    """Takes in a list of players and then outputs
    100 different lineup possibilities"""
    samples = []
    with open('../data/player2sim_fd.pkl', 'rb') as f:
        player2sim = pickle.load(f)

    for player in player_lst:
        samples.append(player2sim[player])

    samples = np.array(samples)
    totals = np.sum(samples, axis=0)
    return totals


if __name__ == '__main__':
    players = ['Lillard, Damian', 'Simmons, Ben',
               'Bradley, Avery', 'Miles, C.J.',
               'Vonleh, Noah',  'Clark, Ian',
               'Bembry, DeAndre', 'Brown, Jaylen']

    print(create_lineup_dist(players))
    # df = load_file('web_deploy/2018-2019_dk.csv')
    #
    # df['fd_pt'] = 3*df['threes'].astype('int8') + \
    #     2*(df['fg_made'].astype('int8') - df['threes'].astype('int8')) + \
    #     df['ft_made'].astype('int8') + \
    #     1.2*df['rebounds'].astype('int8') + \
    #     1.5*df['assists'].astype('int8') + \
    #     3*df['blocks'].astype('int8') + 3*df['steals'].astype('int8') - \
    #     df['turnovers'].astype('int8')
    #
    # players = df['player'].unique()
    # print(make_team_hist(players, 'fd', df))
