import pandas as pd
import numpy as np
from collections import Counter


class DfsData:
    def __init__(self, day, dfs_name):
        self.day = day
        self.dfs_name = dfs_name
        if dfs_name == "fanduel":
            self.df = pd.read_csv("data/2018-2019_fd.csv")\
               .drop("Unnamed: 0", axis=1)
        elif dfs_name == "draftkings":
            self.df = pd.read_csv("data/2018-2019_dk.csv")\
               .drop("Unnamed: 0", axis=1)
        else:
            self.df = None
        # Filter out records after the setting day
        self.df = self.df[self.df['date'] <= day]
        self.df_today = None
        self.player_display_dict = None
        if dfs_name == "fanduel":
            self.selected = {"PG": ["", ""],
                             "SG": ["", ""],
                             "SF": ["", ""],
                             "PF": ["", ""],
                             "C": [""]}
            self.lineup = ["pg1", "pg2",
                           "sg1", "sg2",
                           "sf1", "sf2",
                           "pf1", "pf2",
                           "c1"]
            self.remain_budget = 60000
        else:
            self.selected = {"PG": [""],
                             "SG": [""],
                             "SF": [""],
                             "PF": [""],
                             "C": [""],
                             "G": [""],
                             "F": [""],
                             "UTIL": [""]}
            self.lineup = ["pg1",
                           "sg1",
                           "sf1",
                           "pf1",
                           "c1",
                           "g1",
                           "f1",
                           "util1"]
            self.remain_budget = 50000

    def select(self, select_pool, select_index, to_change_order=None):
        """
        Add player info into self.selected and do repetition check
        :param select_pool: which category to select, e.x. PG
        :param select_index: which index in select_pool to choose, e.x. 0
        :param to_change_order: which slot from 1-9 to change on lineup,
                                (1-8 for draftkings)
                                if None, choose the first one in category
        :return: True if successfully selected,
                 False otherwise (target player not found /
                 already selected / etc.)
        """
        # Check if target player is valid
        if select_pool.upper() not in self.player_display_dict:
            print("select_pool must be in {}"
                  .format(list(self.selected.keys())))
            return False
        if len(self.player_display_dict[select_pool.upper()]) < \
                select_index + 1:
            print("select_index outside of available players")
            return False

        target_player = \
            self.player_display_dict[select_pool.upper()][select_index]

        # Check which place in the category to replace
        if not to_change_order:
            select_tag = "{}{}".format(select_pool.lower(), 1)
            inner_order = 1
        else:
            select_tag = self.lineup[int(to_change_order)-1]
            inner_order = int(select_tag[-1])
        inner_index = inner_order - 1

        # Check if target player is already chosen in other positions
        for key, item in self.selected.items():
            for i in range(len(item)):
                if type(item[i]) == type(target_player) and \
                        target_player['player'].lower() == \
                        item[i]['player'].lower() and \
                        (key.lower() != select_pool.lower()
                         or inner_index != i):
                    print("target player already chosen")
                    return False

        # Check if budget is enough
        if type(self.selected[select_pool.upper()][inner_index]) == \
                type(target_player):
            potential_budget = self.remain_budget + \
                self.selected[select_pool.upper()][inner_index]['salary']
        else:
            potential_budget = self.remain_budget
        if target_player['salary'] > potential_budget:
            print("Remaining budge not enough")
            return False

        # Add/Replace the player
        if type(self.selected[select_pool.upper()][inner_index]) == \
                type(target_player):
            self.remain_budget += \
                self.selected[select_pool.upper()][inner_index]['salary']
        self.remain_budget -= target_player['salary']
        self.selected[select_pool.upper()][inner_index] = target_player
        return True

    def name_adjust(self):
        """
        Create the 'name' column for display
        For example, Dion Waiters would be 'D. Waiters'
        :return: original dataframe + 'player_dis' column
        """
        self.df["last_name"] = self.df["player"]\
            .apply(lambda x: x.split(', ')[0])
        self.df["first_name_init"] = self.df["player"]\
            .apply(lambda x: x.split(', ')[1][0])
        self.df["player_dis"] = self.df["first_name_init"] + '. ' + \
            self.df["last_name"]
        return self.df

    def fetch_match(self):
        """
        Create the 'match' column for display
        :return: original dataframe + 'match' column
        """
        self.df["team"] = self.df["team"].apply(lambda x: x.upper())
        self.df["opponent"] = self.df["opponent"].apply(lambda x: x.upper())
        self.df["match"] = ""
        self.df["match"][self.df.away == np.False_] = self.df["opponent"] + \
            '@' + self.df["team"]
        self.df["match"][self.df.away == np.True_] = self.df["team"] + '@' + \
            self.df["opponent"]
        return self.df

    def get_today_info(self):
        """
        Get today's info for display in dashboard
        :return: dataframe with info for display
        """
        if self.df_today is not None:
            return self.df_today

        prev_played_dict = \
            Counter(self.df[self.df['date'] < self.day]["player"])
        self.df = self.name_adjust()
        self.df = self.fetch_match()
        self.df_today = self.df[self.df['date'] == self.day][["player",
                                                              "player_dis",
                                                              "position",
                                                              "team",
                                                              "salary",
                                                              "match",
                                                              "away"]]
        self.df_today["game_played"] = self.df_today["player"]\
            .apply(lambda x: prev_played_dict[x])
        self.df_today["salary_dis"] = self.df_today["salary"]\
            .apply(lambda x: '${:,}'.format(x))
        self.df_today["player_link"] = self.df_today["player"]\
            .apply(lambda x: x.split(", "))\
            .apply(lambda x: x[1] + "-" + x[0])
        return self.df_today

    def generate_pos_info(self, position):
        """
        Create a list of players' info according to the position
        :param position: [PG, SG, SF, PF, C]
                        if it's draftkings, it can also be G, F, and Util
        :return: a list of positional players and their info
                in descending order of salary
        """
        if self.df_today is None:
            self.get_today_info()
        if position == "UTIL":
            pos_df = self.df_today.sort_values(by="salary", ascending=False)
        else:
            pos_df = \
                self.df_today[self.df_today["position"]
                              .str.contains(position)]\
                .sort_values(by="salary", ascending=False)
        df_length = len(pos_df)
        player_list = []
        for i in range(df_length):
            player_info = pos_df.iloc[i, :]
            player_list.append(player_info)
        return player_list

    def create_dashboard_display_dict(self):
        """
        Create a dictionary of players' info
        For example, if I want to get all the SF's for today,
        I can just call player_display_dict['SF']
        :return: a dictionary that has today's players' info
        """
        if self.player_display_dict:
            return self.player_display_dict
        position_list = ["PG", "SG", "SF", "PF", "C"]
        if self.dfs_name == "draftkings":
            position_list.append('G')
            position_list.append('F')
            position_list.append('UTIL')
        self.player_display_dict = {}
        for position in position_list:
            self.player_display_dict[position] = \
                self.generate_pos_info(position)
        return self.player_display_dict
