import pandas as pd

#############################################
# Finding the players with the highest floors
#############################################


def projection_floor(player_row: pd.Series):
    """Take in the player name 'LastN, FirstN' and projections
    Returns the minimum projection by all sites"""
    floor = min([player_row['proj_FanDuel'],
                 player_row['proj_DraftKings'],
                 player_row['proj_FantasyDraft'],
                 player_row['proj_Draft'],
                 player_row['proj_Yahoo']])
    return floor


def optimal_lineup(projections: pd.DataFrame):
    player_to_floor = {}
    for row in projections.iterrows():
        player_to_floor[row[1]['player']] = projection_floor(row[1])
    return player_to_floor


if __name__ == '__main__':
    proj_df = pd.read_csv('fake_projections.csv')
    print(optimal_lineup(proj_df))
