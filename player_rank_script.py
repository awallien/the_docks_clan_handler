import datetime
import heapq
import pandas as pd
import pathlib

from osrs_api import Hiscores, const
from prompt_args import *
from argparse import ArgumentParser
from logger import debug_set_enable, debug_print

class PlayerHandler:

    CMB_SKILLS = ['attack', 'defence', 'strength', 'magic', 'ranged']
    MELEE_CMB_SKILLS = ['attack', 'defence', 'strength']
    NEW_PLAYER_RANKS = [1,2]
    ACTIVENESS_RANKS = [3,4]
    ACHIEVEMENT_RANKS = [5,6,7,8,9,10]
    HONOR_RANKS = [11,12,13,14]

    def __init__(self, player) -> None:
        assert(isinstance(player, Hiscores))
        self.player: Hiscores = player

    def get_new_player_rank(self):
        max_levels_info = self.get_max_levels_info()
        if max_levels_info["rank"] >= 7:
            return 2
        return 1
        
    def get_max_levels_info(self):
        skills = {"combat": {}, "other": {}}

        for skill_name,skill_obj in self.player.skills.items():
            if skill_name in self.CMB_SKILLS:
                skills["combat"][skill_name] = skill_obj.level
            elif skill_name != "hitpoints":
                skills["other"][skill_name] = skill_obj.level

        melee_lvls = [(name,skills["combat"][name]) for name in self.MELEE_CMB_SKILLS]
        melee_max_lvl = max(melee_lvls, key=lambda x: x[1])
        ranged_lvl = ("ranged", skills["combat"]["ranged"])
        magic_lvl = ("magic", skills["combat"]["magic"])
        cmb_avg = self.calc_avg(melee_max_lvl[1], ranged_lvl[1], magic_lvl[1])

        max_others = heapq.nlargest(3, skills["other"].items(), key=lambda x: x[1]) 
        others_avg = self.calc_avg(*[other[1] for other in max_others])        

        return ({
            "cmb": {"melee": melee_max_lvl, "ranged": ranged_lvl, "magic": magic_lvl},
            "other": {name:lvl for name,lvl in max_others},
            "avg": {"cmb": cmb_avg, "other": others_avg},
            "rank": max(cmb_avg//10, others_avg//10) + 1
        })

    @staticmethod
    def calc_avg(*args): 
        return sum(args)//len(args)


class ClanDatabase:
    
    cache_db_file = str(pathlib.Path(__file__).parent.absolute()) + "/cache/cache_db.csv"
    MEMBER = "Member"
    RANK = "Rank"
    JOINED = "Joined"
    PARENT = "Parent"
    ACTIVE = "Active"
    TOTAL_XP = "Total XP"

    def __init__(self, data_file=None, mode_chr="w") -> None:
        self.db : pd.DataFrame = None
        self.mode_chr = mode_chr
        self.column_headers = [
            self.MEMBER,
            self.RANK,
            self.JOINED,
            self.PARENT,
            self.ACTIVE,
            self.TOTAL_XP
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

        new_player_data = {self.MEMBER: player_name, self.RANK: rank, self.JOINED: joined_date}
        if parent:
            new_player_data[self.PARENT] = parent
        if total_xp:
            new_player_data[self.TOTAL_XP] = total_xp

        new_player_data_df = pd.DataFrame([new_player_data])
        self.db = pd.concat([self.db, new_player_data_df], ignore_index=True)
        
        return RESPONSE_OK

    def update_player(self, player, new_name=None, new_rank=None, total_xp=None):
        if player not in self.db[self.MEMBER].values:
            return RESPONSE_ERR(f"Player name {player} does not exist in clan")
        
        if new_name:
            self.db.loc[self.db.Member == player, self.MEMBER] = new_name
        if new_rank:
            self.db.loc[self.db.Member == player, self.RANK] = new_rank
        if total_xp:
            self.db.loc[self.db.Member == player, self.TOTAL_XP] = total_xp
        
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

    def get_data(self, player, column):
        return self.db[self.db.Member == player, column]

    def dump(self):
        print(self.db.to_string())


class ClanRankScriptHandler(PromptRunner):
    def __init__(self, clan_db):
        if clan_db == None:
            raise ValueError("Clan DB must be of type ClanDatabase and must NOT be None")

        self.clan_db : ClanDatabase = clan_db
        self.banner = "The Docks Rank Script v1.0"
        self.cmds = {
            "addplayer": PromptArgs("addplayer", self.cb_add_player, "add new player to db", ["player"], ["joined", "parent"]),
            "updateplayer": PromptArgs("updateplayer", self.cb_update_player, "update player's info in db", ["player"], ["name", "rank"]),
            "deleteplayer": PromptArgs("deleteplayer", self.cb_delete_player, "delete player from db", ["player"]),
            "appendfiledb": PromptArgs("appendfiledb", self.cb_append_db, "append new data from file to cache db", ["file"]),
            "savedb": PromptArgs("savedb", self.cb_save_db, "save cache db to cache file"),
            "downloaddb": PromptArgs("downloaddb", self.cb_download, "download db to csv file", ["file"]),
            "updatedb": PromptArgs("updatedbxp", self.cb_update_db, "update all players' info in db"),
            "dumpdb": PromptArgs("dumpdb", self.cb_dump_db, "dump cache db")
        }

        super().__init__(self.cmds, banner=self.banner)

    @staticmethod
    def player_hiscore_get(p_name):
        try:
            p_hiscore = Hiscores(p_name, const.AccountType.NORMAL)
            return p_hiscore
        except Exception as e:
            return None

    def cb_add_player(self, args):
        player = args.player
        joined_date = args.joined
        parent = args.parent
        rank = 1
        
        player_hiscore = self.player_hiscore_get(player)
        total_xp = -1
        if not player_hiscore:
            debug_print("Player not found in hiscore db, just add to cache db with Rank 1")
        else:
            player_info = PlayerHandler(player_hiscore)
            rank = player_info.get_new_player_rank()
            total_xp = player_hiscore.total_xp

        return self.clan_db.add_new_player(player, rank, joined_date, parent, total_xp=total_xp)
    
    def cb_update_player(self, args):
        player = args.player
        new_name = args.name
        rank = args.rank
        return self.clan_db.update_player(player, new_name, rank)

    def cb_delete_player(self, args):
        player = args.player
        return self.clan_db.delete_player(player)

    @default_response_ok
    def cb_dump_db(self, _):
        self.clan_db.dump()

    def cb_save_db(self, _):
        res = self.clan_db.save_to_cache()
        return res

    def cb_append_db(self, args):
        data_file = args.file
        res = self.clan_db.append_file_to_cache(data_file)
        return res
    
    def cb_download(self, args):
        write_file = args.file
        res = self.clan_db.write_to_file(write_file)
        return res
    
    def __cb_update_db_total_xp(self, player):
        total_xp = -1
        hiscore = self.player_hiscore_get(player)
        if hiscore and hiscore.total_xp:
            total_xp = hiscore.total_xp
        self.clan_db.update_player(player, total_xp=total_xp)
        return RESPONSE_OK
    
    def __cb_update_db_rank(self, player):
        pass


    def cb_update_db(self, _):
        update_cbs = [
            self.__cb_update_db_total_xp,

        ]

if __name__ == "__main__":
    parser = ArgumentParser(
        prog="player_rank_script.py",
        description="The Docks Ranking Script",
        allow_abbrev=False
    )

    parser.add_argument('-f', metavar="csv file", type=str, default="",
                        help="data file of clan members (name,rank,date_joined,parent)")
    
    parser.add_argument('-d', action="store_true", default=False, 
                        help="enable debug info")
    
    parser.add_argument('-m', metavar="(w|a)", type=str, default="w",
                        help="mode of writing data file (-f) to cache db"
                             "'w' (default) for overriding cache db"
                             "'a' append data from file to existing cache db")
    
    args = parser.parse_args()

    if args.m != 'w' and not args.f:
        print("Mode argument (-m) must be accompanied with a Data File argument (-f)")
        exit(0)

    debug_set_enable(args.d)
    debug_print("Debug info is turned ON")

    db = ClanDatabase(args.f, args.m)
    handler = ClanRankScriptHandler(db)
    
    try:
        handler.run()
    except EOFError and KeyboardInterrupt:
        exit(0)



    
    