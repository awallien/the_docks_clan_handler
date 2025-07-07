
from service import ClanMemberService
from logging import DEBUG, ERROR
from db import DataFrameDatabaseDirCache, DataFrameDatabase
from dao import ClanMemberFields
from util import set_logger_level, Hiscore
from .mgmt_abc import ICallbackMapper
from .mgmt_util import convert_to_datetime

# @db_is_loaded
# @db_lock
# def show_clan_members_cb(**kwargs):
#     if 'name' in kwargs:
#         members = docks_clan_cb.clan_member_service.get_member(kwargs['name'])
#     else:
#         joined_date = kwargs.get('joined_date', None)
#         rank = kwargs.get('rank', None)
#         total_xp = kwargs.get('total_xp', None)
#         last_rank_date = kwargs.get('last_rank_date', None)
#         filter_query = docks_clan_cb.build_query(
#             joined_date=joined_date,
#             rank=rank,
#             total_xp=total_xp,
#             last_rank_date=last_rank_date
#         )
#         members = docks_clan_cb.clan_member_service.get_members(filter_query)
    
#     for member in members:
#         print(f"{member.member}, {member.joined_date}, {member.rank}")

# @db_lock
# def show_db_cache_cb(_) -> None:
#     db_cache_list = docks_clan_cb.cache.cache_list()
#     print(db_cache_list)


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
        
        if not name or not (joined_date := convert_to_datetime(joined_date)):
            return False
        
        return self._clan_member_service.add_member(name, joined_date)

    def update_member(self, name, joined_date, rank, total_xp):
        if not self._db or not self._clan_member_service:
            return False
        
        return self._clan_member_service.update_member(name, joined_date, rank, total_xp)

    def delete_member(self, name):
        if not self._db or not self._clan_member_service:
            return False
        
        return self._clan_member_service.delete_member(name)
    
    def get_member(self, name, show_stat):
        if not self._db or not self._clan_member_service:
            return False
        
        clan_info = self._clan_member_service.get_member(name)
        if not clan_info:
            return False
        
        return Hiscore(name) if show_stat else "N/A"

    def get_members(self, joined_date, rank, total_xp, last_rank_date):
        if not self._db or not self._clan_member_service:
            return False
        
        query = ""

        if joined_date:
            if not (joined_date := convert_to_datetime(joined_date)):
                return False
            query += "Joined_Date"

    def show_database_cache(self):
        return self._cache.cache_list()

cbs = _DocksClanCommandsCallback()

def new_db_cb(**kwargs):
    return cbs.new_database()

def save_db_cb(**kwargs):
    fname = kwargs.get("name", "")
    if not fname:
        return False
    
    return cbs.save_database(fname)

def load_db_cb(**kwargs):
    fname = kwargs.get("name", "")
    f_idx = kwargs.get("index", -1)
    return cbs.load_database(fname, f_idx)

def delete_db_cb(**kwargs):
    fname = kwargs.get("name", "")
    f_idx = kwargs.get("index", -1)
    return cbs.delete_database(fname, f_idx)

def add_clan_member_cb(**kwargs):
    name = kwargs.get("name", "")
    joined_date = kwargs.get("joined_date", "")
    return cbs.add_member(name, joined_date)

def update_clan_member_cb(**kwargs):
    name = kwargs.get("name", "")
    joined_date = kwargs.get("joined_date", "")
    rank = kwargs.get("rank", "")
    total_xp = kwargs.get("total_xp", "")
    cbs.update_member(name, joined_date, rank, total_xp)

def delete_clan_member_cb(**kwargs):
    name = kwargs.get("name", "")
    return cbs.delete_member(name)

def debug_cb(**kwargs):
    name = kwargs.get("name", "")
    enable = kwargs.get("enable", False)
    if enable:
        return set_logger_level(DEBUG, name)
    else:
        return set_logger_level(ERROR, name)

def show_clan_member_cb(**kwargs):
    name = kwargs.get("name", "")
    stat = kwargs.get("stat", None)
    return cbs.get_member(name, stat)

def show_clan_members_cb(**kwargs):
    joined_date = kwargs.get("joined_date", "")
    rank = kwargs.get("rank", "")
    total_xp = kwargs.get("total_xp", "")
    last_rank_date = kwargs.get("last_rank-date", "")
    return cbs.get_members(joined_date, rank, total_xp, last_rank_date)

def show_db_cache_cb(**kwargs):
    return cbs.show_database_cache()

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
    cbs.register(mapper_fn)
