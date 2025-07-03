
from datetime import datetime
from service import ClanMemberService

from db import DataFrameDatabaseDirCache, DataFrameDatabase
from dao import ClanMemberFieldsEnum
from .mgmt_abc import ICallbackMapper
from .mgmt_util import convert_to_datetime

class _DocksClanCommandsCallback(ICallbackMapper):

    def __init__(self):
        self._cache: DataFrameDatabaseDirCache          = DataFrameDatabaseDirCache()
        self._clan_member_service: ClanMemberService    = None
        self._current_db: DataFrameDatabase             = None
        super().__init__()

    @property
    def clan_member_service(self):
        return self._clan_member_service
    
    @property
    def cache(self):
        return self._cache 

    def new_database(self):
        if self.db_is_loaded():
            resp = input(
                "A database is already loaded. Do you want to save your current one? (y/n): "
            ).strip().lower()
            if resp == 'y':
                fname = input("Enter the filename to save the current database: ").strip()
                if not self.save_database(fname):
                    print("Failed to save the current database.")
                    return False
        self._clan_member_service = ClanMemberService()
        self._current_db = self._clan_member_service.get_db()
        return True


    def save_database(self, fname: str) -> bool:
        """Save current database to file"""
        if not fname:
            return False
        
        if self._current_db is None:
            return False
        
        return self.cache.save(fname=fname, db=self._current_db)

    def load_database(self, fname: str, cache_f_idx: int = -1) -> bool:
        """Load database from file"""
        if not (fname or cache_f_idx >= 0):
            return False
        
        cols = ClanMemberFieldsEnum
        self._current_db = self.cache.load(cols, fname=fname, cache_f_idx=cache_f_idx)
        
        return self._current_db is not None

    def db_is_loaded(self) -> bool:
        return self._current_db is not None
        

docks_clan_cb = _DocksClanCommandsCallback()


def db_is_loaded(**kwargs) -> bool:
    return docks_clan_cb.db_is_loaded()


def add_clan_member_cb(**kwargs) -> bool:
    name = kwargs.get('name', None)
    joined_date = kwargs.get('joined_date', None)

    if not (name and joined_date):
        return False

    return docks_clan_cb.clan_member_service.add_member(name, joined_date)


def update_clan_member_cb(**kwargs) -> bool:
    if not (name := kwargs.get('name', None)):
        return False
    joined_date = kwargs.get('joined_date', None)
    rank = kwargs.get('rank', None)
    total_xp = kwargs.get('total_xp', None)
    docks_clan_cb.clan_member_service.update_member(
        name=name,
        joined_date=convert_to_datetime(joined_date) if joined_date else None,
        rank=rank,
        total_xp=total_xp,
    )
    return True


def delete_clan_member_cb(**kwargs) -> bool:
    if not (name := kwargs.get('name', None)):
        return False
    return docks_clan_cb.clan_member_service.delete_member(kwargs['name'])


def new_db_cb(**kwargs) -> bool:
    return docks_clan_cb.new_database()

def save_db_cb(**kwargs):
    fname = kwargs.get('name', None)
    if not fname:
        return False
    return docks_clan_cb.save_database(fname)

def load_db_cb(**kwargs):
    fname = kwargs.get('name', None)
    cache_f_idx = kwargs.get('cache_f_idx', -1)
    if not (fname or cache_f_idx >= 0):
        return False
    return docks_clan_cb.load_database(fname=fname, cache_f_idx=cache_f_idx)

def show_clan_members_cb(**kwargs):
    if 'name' in kwargs:
        members = docks_clan_cb.clan_member_service.get_member(kwargs['name'])
    else:
        joined_date = kwargs.get('joined_date', None)
        rank = kwargs.get('rank', None)
        total_xp = kwargs.get('total_xp', None)
        last_rank_date = kwargs.get('last_rank_date', None)
        filter_query = docks_clan_cb.build_query(
            joined_date=joined_date,
            rank=rank,
            total_xp=total_xp,
            last_rank_date=last_rank_date
        )
        members = docks_clan_cb.clan_member_service.get_members(filter_query)
    
    for member in members:
        print(f"{member.member}, {member.joined_date}, {member.rank}")


def show_db_cache_cb(_) -> None:
    db_cache_list = docks_clan_cb.cache.cache_list()
    print(db_cache_list)


def debug_cb(**kwargs):
    pass


""" Register Commands """
_internal_mapper_fns = [
    db_is_loaded,
    add_clan_member_cb,
    update_clan_member_cb,
    delete_clan_member_cb,
    save_db_cb,
    load_db_cb,
    debug_cb,
    show_clan_members_cb,
    show_db_cache_cb,
    new_db_cb
]

for mapper_fn in _internal_mapper_fns:
    docks_clan_cb.register(mapper_fn)
