
from typing import Optional
from service import ClanMemberService, rank_service
from logging import DEBUG, ERROR
from db import DataFrameDatabaseDirCache, DataFrameDatabase
from dao import ClanMemberFields
from util import set_logger_level, Hiscore
from .mgmt_abc import ICallbackMapper
from .mgmt_util import _convert_from_ordinal, get_leaf_values, print_hiscore_stats


class _DocksClanCommandsCallback(ICallbackMapper):

    def __init__(self):
        self._cache: DataFrameDatabaseDirCache          = DataFrameDatabaseDirCache()
        self._clan_member_service: ClanMemberService    = None
        self._db: DataFrameDatabase                     = None
        super().__init__()


    def new_database(self):
        self._db = DataFrameDatabase(prim_cols=ClanMemberFields.primary(),
                                     cols = ClanMemberFields.values(),
                                     prim_cols_sort_fn=ClanMemberFields.primary_sort)
        self._clan_member_service = ClanMemberService(self._db)
        return "New DB is created."

    def save_database(self, fname):
        if not self._db or not fname:
            return False

        return self._cache.save(self._db, fname)

    def load_database(self, f_name: str = "", f_idx: int = -1):
        if not (f_name or f_idx >= 0):
            return False
        
        self._db = self._cache.load(ClanMemberFields, f_name, f_idx)
        if not self._db:
            return False
        
        self._clan_member_service = ClanMemberService(self._db)
        return True

    def delete_database(self, f_name: str = "", f_idx: int = -1):
        if not self._db:
            return False
        
        if not (f_name or f_idx >= 0):
            return False
        
        return self._cache.delete(f_name, f_idx)

    def add_member(self, name, joined_date):
        if not self._db or not self._clan_member_service:
            return False
        
        if not name or not joined_date:
            return False
        
        return self._clan_member_service.add_member(name, joined_date)

    def update_member(self, name, joined_date=0, rank=0, total_xp=0):
        if not self._db or not self._clan_member_service:
            return False

        clan_member = self._clan_member_service.get_member(name)
        if not clan_member:
            return False

        cm_rank = clan_member.rank
        cm_joined_date = clan_member.joined_date
        cm_total_xp = clan_member.total_xp

        hiscore = self._get_hiscore(name)

        # If any of joined_date, rank, or total_xp are missing → perform a full update
        if not all([joined_date, rank, total_xp]):
            new_rank = rank_service.get_next_rank(hiscore, cm_rank, cm_joined_date)
            new_total_xp = hiscore.total_xp if hiscore else 0
            return self._clan_member_service.update_member(name, cm_joined_date, new_rank, new_total_xp)

        # Partial update: use provided values or fall back to current ones
        return self._clan_member_service.update_member(
            name,
            joined_date or cm_joined_date,
            rank or cm_rank,
            total_xp or cm_total_xp
        )

    def delete_member(self, name):
        if not self._db or not self._clan_member_service:
            return False
        return self._clan_member_service.delete_member(name)
    
    def get_member(self, name, show_stat):
        if not self._db or not self._clan_member_service:
            return False
        
        member = self._clan_member_service.get_member(name)
        if not member:
            return False

        joined_date = _convert_from_ordinal(member.joined_date)
        last_rank_date = _convert_from_ordinal(member.last_rank_date)
        print(f"Name            Joined Date    Rank     Total XP     Last Rank Date\n"
               "----            -----------    ----     --------     --------------\n"
               f"{member.member:<15} {joined_date:<14} {member.rank:<8} {member.total_xp:<12} {last_rank_date}\n")

        if show_stat:
            print_hiscore_stats(name)         

        return True

    def get_members(self, query):
        if not self._db or not self._clan_member_service:
            return False
        
        members = self._clan_member_service.get_members(query)
        print(f"Name            Joined Date    Rank     Total XP     Last Rank Date\n"
               "----            -----------    ----     --------     --------------")
        for member in members:
            joined_date = _convert_from_ordinal(member.joined_date)
            last_rank_date = _convert_from_ordinal(member.last_rank_date)
            print(f"{member.member:<15} {joined_date:<15} {member.rank:<8} {member.total_xp:<12} {last_rank_date}")

        return True

    def show_database_cache(self):
        return self._cache.cache_list()
    
    @staticmethod
    def _get_hiscore(name: str) -> Optional[Hiscore]:
        try:
            return Hiscore(name)
        except Exception as e:
            print(e)
        return None

docks_clan_cb = _DocksClanCommandsCallback()

def new_db_cb(**kwargs):
    return docks_clan_cb.new_database()

def save_db_cb(**kwargs):
    values = get_leaf_values(["name"], kwargs).results
    fname = values.get("name", "")
    return docks_clan_cb.save_database(fname)

def load_db_cb(**kwargs):
    values = get_leaf_values(["name", "index"], kwargs).results
    fname = values.get("name", "")
    f_idx = values.get("index", -1)
    return docks_clan_cb.load_database(fname, f_idx)

def delete_db_cb(**kwargs):
    values = get_leaf_values(["name", "index"], kwargs).results
    fname = values.get("name", "")
    f_idx = values.get("index", -1)
    return docks_clan_cb.delete_database(fname, f_idx)

def add_clan_member_cb(**kwargs):
    values = get_leaf_values(["name", "joined_date"], kwargs).results
    name = values.get("name", "")
    joined_date = values.get("joined_date", "")
    return docks_clan_cb.add_member(name, joined_date)

def update_clan_member_cb(**kwargs):
    values = get_leaf_values(["name", "joined_date", "rank", "total_xp"], kwargs).results
    name = values.get("name", "")
    joined_date = values.get("joined_date", "")
    rank = values.get("rank", "")
    total_xp = values.get("total_xp", "")
    return docks_clan_cb.update_member(name, joined_date, rank, total_xp)

def delete_clan_member_cb(**kwargs):
    values = get_leaf_values(["name"], kwargs).results
    name = values.get("name", "")
    return docks_clan_cb.delete_member(name)

def debug_cb(**kwargs):
    values = get_leaf_values(["name", "enable"], kwargs).results
    name = values.get("name", "")
    enable = values.get("enable", False)
    if enable:
        return set_logger_level(DEBUG, name)
    else:
        return set_logger_level(ERROR, name)

def show_clan_member_cb(**kwargs):
    values = get_leaf_values(["name", "stat"], kwargs).results
    name = values.get("name", "")
    stat = values.get("stat", False)
    return docks_clan_cb.get_member(name, stat)

def show_clan_members_cb(**kwargs):
    query = get_leaf_values(
        ["joined_date", "rank", "total_xp", "last_rank_date"],
        kwargs,
        build_query=True
    ).query
    return docks_clan_cb.get_members(query)

def show_db_cache_cb(**kwargs):
    return docks_clan_cb.show_database_cache()

""" Register Commands """
_internal_mapper_fns = [
    new_db_cb,
    save_db_cb,
    load_db_cb,
    delete_db_cb,

    add_clan_member_cb,
    update_clan_member_cb,
    delete_clan_member_cb,
    
    debug_cb,

    show_clan_member_cb,
    show_clan_members_cb,
    show_db_cache_cb,
]

for mapper_fn in _internal_mapper_fns:
    docks_clan_cb.register(mapper_fn)
