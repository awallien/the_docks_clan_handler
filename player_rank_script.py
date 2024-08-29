from argparse import ArgumentParser
from util import *
from clan_db import ClanDatabase

class ClanRankScriptHandler(PromptRunner):
    """Handles user's commands"""

    def __init__(self, clan_db):
        if clan_db == None:
            raise ValueError("Clan DB must be of type ClanDatabase and must NOT be None")

        self.clan_db : ClanDatabase = clan_db
        self.banner = "The Docks Rank Script v1.0"
        self.cmds = {
            "addplayer": PromptArgs("addplayer", self.cb_add_player, "add new player to db", ["player"], ["joined", "parent"]),
            "updateplayer": PromptArgs("updateplayer", self.cb_update_player, "update player's info in db", ["player"], ["name", "rank", "parent", "active_cnt", "rank_challenge_attempt"]),
            "deleteplayer": PromptArgs("deleteplayer", self.cb_delete_player, "delete player from db", ["player"]),
            "appendfiledb": PromptArgs("appendfiledb", self.cb_append_db, "append new data from file to cache db", ["file"]),
            "savedb": PromptArgs("savedb", self.cb_save_db, "save cache db to cache file"),
            "downloaddb": PromptArgs("downloaddb", self.cb_download, "download db to csv file", ["file"]),
            "updatedb": PromptArgs("updatedb", self.cb_update_db, "update all players' info in db"),
            "dumpdb": PromptArgs("dumpdb", self.cb_dump_db, "dump cache db", opt_params=["rank"]),
            "dumpplayer": PromptArgs("dumpplayer", self.cb_dump_player, "dump one player in db", ["player"]),
            "updatedbplayer": PromptArgs("updatedbplayer", self.cb_update_db_player, "do one update on player in db", ["player"]),
            "playerstat": PromptArgs("playerstat", self.cb_dump_player_stat, "dump player stat from Hiscore", ["player"])
        }

        super().__init__(self.cmds, banner=self.banner)
    
    @staticmethod
    def __get_total_xp(player_hiscore):
        total_xp = -1
        if player_hiscore and player_hiscore.total_xp:
            total_xp = player_hiscore.total_xp
        return total_xp

    def cb_add_player(self, args):
        player = args.player
        joined_date = args.joined
        parent = args.parent
        rank = 1
        
        player_hiscore = PlayerRankHandler.player_hiscore_get(player)
        if not player_hiscore:
            debug_print("Player not found in hiscore db, just add to cache db with Rank 1")
        else:
            player_info = PlayerRankHandler(player_hiscore)
            rank = player_info.get_new_player_rank()

        return self.clan_db.add_new_player(player, rank, joined_date, parent, total_xp=-1)
    
    def cb_update_player(self, args):
        player = args.player
        new_name = args.name
        rank = args.rank
        parent = args.parent
        rank_challenge_attempt = args.rank_challenge_attempt
        active_cnt = True if str(args.active_cnt).lower() not in ["false", ""] else False
        return self.clan_db.update_player(player, new_name=new_name, new_rank=rank, new_parent=parent, active_cnt=active_cnt, rank_challenge_attempt=rank_challenge_attempt)

    def cb_delete_player(self, args):
        player = args.player
        return self.clan_db.delete_player(player)

    @default_response_ok
    def cb_dump_db(self, args):
        rank = args.rank
        self.clan_db.dump(rank=rank)

    def cb_dump_player(self, args):
        player = args.player
        return self.clan_db.dump(player=player)

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
    
    def cb_update_db_player(self, args):
        player = args.player
        update_fns = [
            self.__cb_update_player_active_xp,
            self.__cb_update_db_rank
        ]
        
        player_hiscore = PlayerRankHandler.player_hiscore_get(player)
        if not player_hiscore:
            err_print(f"!!! No hiscore found for {player}, skip update")
            return RESPONSE_OK

        for update_fn in update_fns:
            player_db_data = self.clan_db.get_player_data(player)
            if player_db_data is None:
                return RESPONSE_ERR(f"Player {player} not found in clan db")
            
            status = update_fn(player, player_hiscore, player_db_data)
            if not status.res:
                return status

            player_db_data = self.clan_db.get_player_data(player)
                
        return status

    def __cb_update_db_rank(self, player, player_hiscore, player_db_data):
        """
        player = get player
        if player::rank in [1,2] and active for one month:
            player::rank = 3
        elif player::rank in [3] and active for one month:
            player::rank = 4
        elif player::rank in [4] and active for one month:
            player::rank = get updated rank(player) -> [5...10]
        elif player::rank in [5-9] and after update:
            player::rank = get updated(rank player) -> player::rank + 1
        """
        player_rank = sanitize_player_rank(player_db_data[ClanDatabase.RANK])
        player_active_cnt = int(player_db_data[ClanDatabase.ACTIVE_CNT])
        player_is_active = (player_active_cnt >= ClanDatabase.ONE_MONTH_ACTIVE)
        new_rank = 0
        status = RESPONSE_OK

        if type(player_rank) == str:
            return status

        if player_rank in PlayerRankHandler.NEW_PLAYER_RANKS:
            if player_is_active:
                new_rank = PlayerRankHandler.ACTIVENESS_RANK_3
                status = self.clan_db.update_player(player, new_rank=new_rank, active_cnt=False)
        elif player_rank == PlayerRankHandler.ACTIVENESS_RANK_3:
            if player_is_active:
                new_rank = PlayerRankHandler.ACTIVENESS_RANK_4
                status = self.clan_db.update_player(player, new_rank=new_rank, active_cnt=False)
        elif (player_rank == PlayerRankHandler.ACTIVENESS_RANK_4 and player_is_active) or \
             player_rank in PlayerRankHandler.ACHIEVEMENT_RANKS:
            player_info = PlayerRankHandler(player_hiscore).get_max_levels_info()
            debug_print(str(player_info))
            new_rank = player_info["rank"]
            status = self.clan_db.update_player(player, new_rank=new_rank, active_cnt=False)
        
        if status.res and new_rank > player_rank:
            print(f"   Player {player} is promoted from rank {player_rank} to {new_rank}")
        
        return status

    def __cb_update_player_active_xp(self, player, player_hiscore, player_db_data):
        """
        if player::rank in [1,2,3,4]:
         let total_xp = hiscore::total_xp
        if total_xp > db::total_xp:
         set active_cnt to 1
        else:
         set active_cnt to 0
        update db with active_cnt and/or total_xp
        """
        player_rank = sanitize_player_rank(player_db_data[ClanDatabase.RANK])
        player_total_xp = self.__get_total_xp(player_hiscore)
        db_total_xp = player_db_data[ClanDatabase.TOTAL_XP]
        status = RESPONSE_OK

        if player_rank in PlayerRankHandler.NEW_PLAYER_RANKS or player_rank in PlayerRankHandler.ACTIVENESS_RANKS:
            active_cnt = False
            if player_total_xp > db_total_xp:
                active_cnt = True
                debug_print(f"{player} total xp: {player_total_xp} > db total xp: {db_total_xp}, active count set to 1")
            else:
                debug_print(f"{player} : no change in total xp, set active count to 0")
        
            status = self.clan_db.update_player(player, active_cnt=active_cnt, total_xp=player_total_xp)
        else:
            status = self.clan_db.update_player(player, total_xp=player_total_xp, active_cnt=True)

        return status
        
    def cb_update_db(self, _):
        update_cbs = [
            self.__cb_update_player_active_xp,
            self.__cb_update_db_rank
        ]

        for member in self.clan_db.get_members():
            member_hiscore = PlayerRankHandler.player_hiscore_get(member)
            member_db_data = self.clan_db.get_player_data(member)

            if member_hiscore is None:
                err_print(f"!!! No hiscore found for {member}, skip update")
                continue

            for update_cb in update_cbs:
                status = update_cb(member, member_hiscore, member_db_data)
                if not status.res:
                    return status
                member_db_data = self.clan_db.get_player_data(member)

        return RESPONSE_OK
    
    @default_response_ok
    def cb_dump_player_stat(self, args):
        player = args.player
        player_hs = PlayerRankHandler.player_hiscore_get(player)
        if player_hs is None:
            print(f"No hiscore for {player}")
        else:
            for skill in SKILLS:
                print(f"{skill}: {player_hs.skills.get(skill).level}")


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
