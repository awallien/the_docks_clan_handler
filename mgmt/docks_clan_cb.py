
from datetime import datetime
from service import ClanMemberService

from .mgmt_abc import ICallbackMapper
from .mgmt_util import convert_to_datetime

class _DocksClanCommandsCallback(ICallbackMapper):

    def __init__(self):
        self._clan_member_service = ClanMemberService()
        super().__init__()

    @property
    def clan_member_service(self):
        return self._clan_member_service

    @classmethod
    def build_query(cls, **kwargs) -> str:
        pass    

docks_clan_cb = _DocksClanCommandsCallback()


def db_is_loaded(**kwargs) -> bool:
    return docks_clan_cb.clan_member_service.db_is_loaded() 


def db_load_is_valid(**kwargs) -> bool:
    name = kwargs.get('name', None)
    index = kwargs.get('index', None)
    if not (bool(name) ^ bool(index)):
        return False
    
    if name:
        return docks_clan_cb.clan_member_service.db_is_loaded()


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


def delete_clan_member_cb(**kwargs) -> bool:
    if not (name := kwargs.get('name', None)):
        return False
    return docks_clan_cb.clan_member_service.delete_member(kwargs['name'])


def new_db_cb(**kwargs):
    pass

def save_db_cb(**kwargs):
    pass


def load_db_cb(**kwargs):
    pass


def debug_cb(**kwargs):
    pass


def show_clan_members_cb(**kwargs):
    if 'name' in kwargs:
        member = docks_clan_cb.clan_member_service.get_member(kwargs['name'])
    else:
        joined_date = kwargs['joined_date']
        rank = kwargs['rank']
        total_xp = kwargs['total_xp']
        last_rank_date = kwargs['last_rank_date']
        filter_query = docks_clan_cb.build_query(joined_date=..., rank=..., total_xp=..., last_rank_date=...)
        members = docks_clan_cb.clan_member_service.get_members(filter_query)


def show_db_cache_cb(_) -> None:
    db_cache_list = docks_clan_cb.clan_member_service.cache_db_list()
    print(db_cache_list)


""" Register Commands """
_internal_mapper_fns = [
    db_is_loaded,
    db_load_is_valid,
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
