import boto3
import pandas as pd
import numpy as np
import pickle
import re
# add TkAgg to avoid crash
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
matplotlib.use("Agg")

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


def create_lineup_dist(player_lst, service, write_path='/tmp/hist.png'):
    """Takes in a list of players and then outputs
    100 different lineup possibilities and write
    it out to the static file"""

    samples = []
    # for sizing things correctly
    my_dpi = 192

    # TODO: Create a player2sim for draft kings
    with open('../../backend/data/player2sim_fd.pkl', 'rb') as f:
        player2sim = pickle.load(f)

    for player in player_lst:
        samples.append(player2sim[player])
    samples = np.array(samples)

    if service == 'fd':
        totals = np.sum(samples, axis=0) - np.min(samples, axis=0)
    else:
        totals = np.sum(samples, axis=0)

    #####################################
    # CREATE DISTRIBUTION PLOT FOR TOTALS
    #####################################
    # prepare the figure to appropriate and clear previous work
    # * the following one line of code may cause crash on OS X
    plt.figure(figsize=(492 / my_dpi, 300 / my_dpi), dpi=my_dpi)
    plt.clf()

    # draw distribution and customize axis label size
    if service == 'fd':
        ax = sns.distplot(totals, color='#0090ff')
    else:
        ax = sns.distplot(totals, color='#9be200')

    plt.xlim((0, 350))
    plt.xlabel('')
    ax.axes.get_yaxis().set_ticklabels([])
    ax.xaxis.label.set_color('w')
    ax.tick_params(axis='x', colors='w')
    plt.rcParams['xtick.labelsize'] = 3
    plt.tick_params(axis='y', which='both', left=False,
                    right=False, labelbottom=False)

    # make the spines white for the black background
    ax.spines['bottom'].set_color('w')
    ax.spines['top'].set_color('w')
    ax.spines['right'].set_color('w')
    ax.spines['left'].set_color('w')

    # write out to disk
    plt.tight_layout()
    plt.savefig(write_path, transparent=True)
    return totals


if __name__ == '__main__':
    players = ['Lillard, Damian', 'Simmons, Ben',
               'Bradley, Avery', 'Miles, C.J.',
               'Vonleh, Noah',  'Clark, Ian',
               'Bembry, DeAndre', 'Brown, Jaylen']

    print(create_lineup_dist(players))
