from datetime import datetime
from enum import Enum, verify, UNIQUE
from typing import Optional, List
from clan_db import *

@verify(UNIQUE)
class ClanMemberFields(Enum):
    MEMBER = "Member"
    JOINED_DATE = "Joined Date"
    RANK = "Rank"
    TOTAL_XP = "Total XP"
    LAST_RANK_DATE = "Last Rank Date"

    @classmethod
    def as_list(cls):
        return list(cls.__members__.keys())
    

class ClanMember(IEntity):
    """Clan Member entity class"""

    def __init__(self, member:str, joined_date:datetime):
        self._member : str                  = member
        self._joined_date : datetime        = joined_date

        self._rank : str                    = ""
        self._total_xp : int                = -1
        self._last_rank_date : datetime     = datetime.min

    @property
    def member(self):
        return self._member
    
    @property
    def rank(self):
        return self._rank
    
    @property
    def joined_date(self):
        return self._joined_date
    
    @property
    def total_xp(self):
        return self._total_xp
    
    @property
    def last_rank_date(self):
        return self._last_rank_date
    
    @member.setter
    def member(self, value):
        self._member = value
    
    @rank.setter
    def rank(self, value):
        self._rank = value
    
    @joined_date.setter
    def joined_date(self, value):
        if not isinstance(value, datetime):
            raise TypeError("ClanMember:joined_date:value is not a datetime:", value)
        self._joined_date = value
    
    @total_xp.setter
    def total_xp(self, value):
        self._total_xp = value

    @last_rank_date.setter
    def last_rank_date(self, value):
        if not isinstance(value, datetime):
            raise TypeError("ClanMember:last_ranked_date:value is not a datetime:", value)
        self._last_rank_date = value


class ClanMemberDFDaoImpl(IDao):
    """Clan Member DAO Impl for DataFrame Database"""

    def __init__(self):
        self.df_db = DataFrameDatabase(key_idx=(ClanMemberFields.MEMBER,), 
                                       columns=ClanMemberFields.as_list(),
                                       key_idx_sort=(lambda member: member.lower()))

    def add(self, obj: ClanMember) -> bool:
        """Add new clan member to DF Database"""
        db_row = DatabaseRow()

        db_row.put(ClanMemberFields.MEMBER, obj.member)
        db_row.put(ClanMemberFields.JOINED_DATE, obj.joined_date)
        db_row.put(ClanMemberFields.RANK, obj.rank)
        db_row.put(ClanMemberFields.TOTAL_XP, obj.total_xp)
        db_row.put(ClanMemberFields.LAST_RANK_DATE, obj.last_rank_date)

        return self.df_db.add_row(db_row)

    def get(self, key: str) -> Optional[ClanMember]:
        """Get clan member from DF Database"""
        contents = self.df_db.get_row(key)
        if contents is None:
            return None
        
        member = contents.get(ClanMemberFields.MEMBER)
        joined_date = contents.get(ClanMemberFields.JOINED_DATE)
        rank = contents.get(ClanMemberFields.RANK)
        total_xp = contents.get(ClanMemberFields.TOTAL_XP)
        last_rank_date = contents.get(ClanMemberFields.LAST_RANK_DATE)

        clan_member = ClanMember(member, joined_date)
        clan_member.rank = rank
        clan_member.total_xp = total_xp
        clan_member.last_rank_date = last_rank_date

        return clan_member

    def update(self, key: str, obj: ClanMember) -> bool:
        """Update clan member info in DF Database"""
        db_row = DatabaseRow()

        db_row.put(ClanMemberFields.MEMBER, obj.member)
        db_row.put(ClanMemberFields.JOINED_DATE, obj.joined_date)
        db_row.put(ClanMemberFields.RANK, obj.rank)
        db_row.put(ClanMemberFields.TOTAL_XP, obj.total_xp)
        db_row.put(ClanMemberFields.LAST_RANK_DATE, obj.last_rank_date)

        return self.df_db.update_row(key, db_row)

    def delete(self, key: str) -> bool:
        """Delete clan member from DF Database"""
        return self.df_db.delete_row(key)

    def get_all(self, filter_expr: str='') -> List[ClanMember]:
        """Get full list of clan members in DF Database"""

        def convert_dict_to_ClanMember(d):
            member = d[ClanMemberFields.MEMBER]
            joined_date = d[ClanMemberFields.JOINED_DATE]
            rank = d[ClanMemberFields.RANK]
            total_xp = d[ClanMemberFields.TOTAL_XP]
            last_rank_date = d[ClanMemberFields.LAST_RANK_DATE]

            clan_member = ClanMember(member, joined_date)
            clan_member.rank = rank
            clan_member.total_xp = total_xp
            clan_member.last_rank_date = last_rank_date

            return clan_member
        
        rows_dict = self.df_db.dump(filter_expr)
        return [convert_dict_to_ClanMember(row) for row in rows_dict]
