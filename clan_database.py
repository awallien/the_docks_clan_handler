import pathlib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from prompt_args import RESPONSE_ERR, RESPONSE_OK
from logger import debug_print, err_print

class ClanDatabase:
    """Handles a clan members' info in a database"""

    cache_db_file = str(pathlib.Path(__file__).parent.absolute()) + "/cache/cache_db.csv"
    ONE_MONTH_ACTIVE = 3
    
    # member's username
    MEMBER = "Member"
    
    # member's rank
    RANK = "Rank"
    
    # date that member joined the clan
    JOINED = "Joined"
    
    # if any, for alt accounts, the original account to a member 
    PARENT = "Parent"
    
    # for members in rank [1..4], are they active in clan? (i.e. total xp is increasing)
    ACTIVE_CNT = "Active Count"
    
    # member's total xp
    TOTAL_XP = "Total XP"

    # last date that a member is promoted
    LAST_RANKED_DATE = "Last Rank Date"

    # rank challenge data for members in honor ranks
    RANK_CHLG_ATTEMPTS = "Rank Challenge Attempts"
    NEXT_RANK_CHLG_DATE = "Next Rank Challenge Date"

    def __init__(self, data_file=None, mode_chr="w") -> None:
        self.db : pd.DataFrame = None
        self.mode_chr = mode_chr
        self.column_headers = [
            self.MEMBER,
            self.RANK,
            self.JOINED,
            self.PARENT,
            self.ACTIVE_CNT,
            self.TOTAL_XP,
            self.LAST_RANKED_DATE,
            self.RANK_CHLG_ATTEMPTS,
            self.NEXT_RANK_CHLG_DATE,
        ]
        self.__init_db(data_file)
    
    def __init_db(self, data_file=None):
        """
            if data file is passed in args,
                if cache already exists
                 if mode is overwrite
                    warn user
                    if yes, override the cache db
                 if mode is append
                    update cache db with new data
                else
                 write data file to cache db
            add missing column headers to cache db
            retrieve cache db and store in obj db
        """
        cache_db = None
        cache_db_path = pathlib.Path(self.cache_db_file)
        if data_file:
            if cache_db_path.is_file():                    
                if self.mode_chr == 'w':
                    resp = input("WARNING!!! Cache DB exists. Are you sure you want to overwrite? [y/n] ")
                    if resp == 'y':
                        cache_db = pd.read_csv(data_file)
                    else:
                        cache_db = pd.read_csv(self.cache_db_file)
                elif self.mode_chr == 'a':
                    self.db = pd.read_csv(self.cache_db_file)
                    self.append_file_to_cache(data_file)
                    self.save_to_cache()
                    return
                else:
                    cache_db = pd.read_csv(self.cache_db_file)
        else:
            cache_db = pd.read_csv(self.cache_db_file)

        self.db = cache_db
        for header in self.column_headers:
            if header not in self.db.columns:
                self.db[header] = np.nan
                self.db[header].fillna(0, inplace=True)
        self.save_to_cache()

    def append_file_to_cache(self, data_file):
        if not pathlib.Path(data_file).is_file():
            return RESPONSE_ERR(f"data file '{data_file}' does not exist")
        
        data_file_db = pd.read_csv(data_file)
        self.db = pd.concat([self.db, data_file_db], ignore_index=True)
        self.db = self.db.drop_duplicates(subset=["Member"], keep="last").reset_index(drop=True)
        
        return RESPONSE_OK

    def save_to_cache(self):
        return self.write_to_file(self.cache_db_file)
    
    def write_to_file(self, write_file):
        if self.db is None:
            return RESPONSE_ERR("Cannot write a None Cache DB")
        
        self.db.to_csv(write_file, sep=",", index=False)
        debug_print(f"Successfully write Cache DB to {write_file}")

        return RESPONSE_OK
    
    def add_new_player(self, player_name, rank=1, joined_date=None, parent=None, total_xp=None):
        if player_name in self.db[self.MEMBER].values:
            return RESPONSE_ERR(f"Player name {player_name} already exists in clan")

        if parent and parent not in self.db[self.MEMBER].values:
            return RESPONSE_ERR(f"Player name {parent} does not exist in clan")

        if joined_date == None:
            joined_date = datetime.now().strftime("%d-%b-%Y")

        new_player_data = {
            self.MEMBER: player_name, 
            self.RANK: rank, 
            self.JOINED: joined_date, 
            self.ACTIVE_CNT: 0,
            self.LAST_RANKED_DATE: 0,
            self.RANK_CHLG_ATTEMPTS: 0,
            self.NEXT_RANK_CHLG_DATE: 0,
        }

        if parent:
            new_player_data[self.PARENT] = parent
        if total_xp:
            new_player_data[self.TOTAL_XP] = total_xp

        new_player_data_df = pd.DataFrame([new_player_data])
        self.db = pd.concat([self.db, new_player_data_df], ignore_index=True)
        
        return RESPONSE_OK

    def update_player(self, player, new_name=None, new_rank=None, total_xp=None, new_parent=None, active_cnt=None, rank_challenge_attempt=None):
        if player not in self.db[self.MEMBER].values:
            return RESPONSE_ERR(f"Player name {player} does not exist in clan")
        
        if new_name:
            self.db.loc[self.db.Member == player, self.MEMBER] = new_name
            debug_print(f"Update {player} to new name {new_name}")
            player = new_name
        if new_rank:
            self.db.loc[self.db.Member == player, self.RANK] = new_rank
            self.db.loc[self.db.Member == player, self.LAST_RANKED_DATE] = datetime.now().strftime("%d-%b-%Y")
            self.db.loc[self.db.Member == player, self.RANK_CHLG_ATTEMPTS] = 0
            self.db.loc[self.db.Member == player, self.NEXT_RANK_CHLG_DATE] = 0.0
        if total_xp:
            self.db.loc[self.db.Member == player, self.TOTAL_XP] = total_xp
        if new_parent:
            self.db.loc[self.db.Member == player, self.PARENT] = new_parent
        if not (active_cnt is None):
            if active_cnt:
                self.db.loc[self.db.Member == player, self.ACTIVE_CNT] += 1
            else:
                self.db.loc[self.db.Member == player, self.ACTIVE_CNT] = 0 
        if not (rank_challenge_attempt is None):
            if rank_challenge_attempt:
                self.db.loc[self.db.Member == player, self.RANK_CHLG_ATTEMPTS] += 1
            else:
                self.db.loc[self.db.Member == player, self.RANK_CHLG_ATTEMPTS] = 0
            self.db.loc[self.db.Member == player, self.NEXT_RANK_CHLG_DATE] = (datetime.now() + timedelta(days=30)).strftime("%d-%b-%Y")
        
        debug_print(f"Update {player}: {self.db.loc[self.db.Member == player].to_string(header=False, index=False)}")
        
        return RESPONSE_OK

    def delete_player(self, player):
        if player not in self.db[self.MEMBER].values:
            return RESPONSE_ERR(f"Player name {player} does not exist in clan")
        
        self.db = self.db[self.db[self.MEMBER] != player]

        return RESPONSE_OK

    def get_members(self):
        if self.db is None:
            return []
        return self.db[self.MEMBER].values

    def get_player_data(self, player):
        if player not in self.db[self.MEMBER].values:
            return None
        return self.db[self.db.Member == player].to_dict('records')[0]
    
    def dump(self, rank=None, player=None):
        if rank:
            print(self.db[self.db[self.RANK] == rank])
        elif player:
            if player not in self.db[self.MEMBER].values:
                return RESPONSE_ERR(f"Player {player} does not exist in clan")
            print(self.db[self.db.Member == player])
        else:
            print(self.db.to_string())

        return RESPONSE_OK