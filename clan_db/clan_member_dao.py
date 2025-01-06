from datetime import datetime
from enum import Enum, verify, UNIQUE
from typing import Optional, List
from clan_db import *

@verify(UNIQUE)
class ClanMemberRankEnum(Enum):
    # INVALID_RANK
    RANK_INVALID = '0'

    # Activeness Ranks
    RANK_1 = '1'; RANK_2 = '2'; RANK_3 = '3'; RANK_4 = '4'

    # Achievement Ranks
    RANK_5 = '5';   RANK_6 = '6';   RANK_7 = '7';   RANK_8 = '8'
    RANK_9 = '9';   RANK_10 = '10'; RANK_11 = '11'; RANK_12 = '12'
    RANK_13 = '13'; RANK_14 = '14'; RANK_15 = '15'
    
    # Honorable Ranks (non-challenged)
    RANK_16 = '16'; RANK_17 = '17'; RANK_18 = '18'
    RANK_19 = '19'; RANK_20 = '20'
    
    # Honorable Ranks (challenged)
    RANK_21 = '21'; RANK_22 = '22'; RANK_23 = '23'
    RANK_24 = '24'

    # Administrative Ranks (A=admin, D=deputy owner, O=owner)
    RANK_A = 'A'; RANK_D = 'D'; RANK_O = 'O'

    @classmethod
    def members(cls):
        return list(cls.__members__.keys())
    
    @classmethod
    def values(cls):
        return list(cls.__members__.values())


@verify(UNIQUE)
class ClanMemberFieldsEnum(Enum):
    MEMBER = DatabaseColumn("Member", "N/A", "string")
    JOIN_DATE = DatabaseColumn("Join_Date", datetime.min, "datetime64[ns]")
    RANK = DatabaseColumn("Rank", ClanMemberRankEnum.RANK_INVALID.name, "category", categories=ClanMemberRankEnum.values())
    TOTAL_XP = DatabaseColumn("Total_XP", -1, "int64")
    LAST_RANK_DATE = DatabaseColumn("Last_Rank_Date", datetime.min, "datetime64[ns]")

    @classmethod
    def members(cls):
        return list(cls.__members__.keys())
    
    @classmethod
    def values(cls):
        return list(cls.__members__.values())

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
        self.df_db = DataFrameDatabase(prim_cols=(ClanMemberFieldsEnum.MEMBER.value,), 
                                       columns=ClanMemberFieldsEnum.values(),
                                       prim_cols_sort_fn=lambda col: col.str.lower())

    def add(self, obj: ClanMember) -> bool:
        """Add new clan member to DF Database"""
        db_row = DatabaseRow()

        db_row.put(ClanMemberFieldsEnum.MEMBER.value, obj.member)
        db_row.put(ClanMemberFieldsEnum.JOIN_DATE.value, obj.joined_date)
        db_row.put(ClanMemberFieldsEnum.RANK.value, obj.rank)
        db_row.put(ClanMemberFieldsEnum.TOTAL_XP.value, obj.total_xp)
        db_row.put(ClanMemberFieldsEnum.LAST_RANK_DATE.value, obj.last_rank_date)

        return self.df_db.add_row(db_row)

    def get(self, key: str) -> Optional[ClanMember]:
        """Get clan member from DF Database"""
        contents = self.df_db.get_row(key)
        if contents is None:
            return None
        
        member = contents.get(ClanMemberFieldsEnum.MEMBER.value)
        joined_date = contents.get(ClanMemberFieldsEnum.JOIN_DATE.value)
        rank = contents.get(ClanMemberFieldsEnum.RANK.value)
        total_xp = contents.get(ClanMemberFieldsEnum.TOTAL_XP.value)
        last_rank_date = contents.get(ClanMemberFieldsEnum.LAST_RANK_DATE.value)

        clan_member = ClanMember(member, joined_date)
        clan_member.rank = rank
        clan_member.total_xp = total_xp
        clan_member.last_rank_date = last_rank_date

        return clan_member

    def update(self, obj: ClanMember) -> bool:
        """Update clan member info in DF Database"""
        db_row = DatabaseRow()

        db_row.put(ClanMemberFieldsEnum.MEMBER.value, obj.member)
        db_row.put(ClanMemberFieldsEnum.JOIN_DATE.value, obj.joined_date)
        db_row.put(ClanMemberFieldsEnum.RANK.value, obj.rank)
        db_row.put(ClanMemberFieldsEnum.TOTAL_XP.value, obj.total_xp)
        db_row.put(ClanMemberFieldsEnum.LAST_RANK_DATE.value, obj.last_rank_date)

        return self.df_db.update_row(db_row)

    def delete(self, obj: ClanMember) -> bool:
        """Delete clan member from DF Database"""
        db_row = DatabaseRow()

        db_row.put(ClanMemberFieldsEnum.MEMBER, obj.member)

        return self.df_db.delete_row(db_row)

    def get_all(self, filter_expr: str='') -> List[ClanMember]:
        """Get full list of clan members in DF Database"""

        def convert_dict_to_ClanMember(d_row):
            member = d_row.get(ClanMemberFieldsEnum.MEMBER.value)
            joined_date = d_row.get(ClanMemberFieldsEnum.JOIN_DATE.value)
            rank = d_row.get(ClanMemberFieldsEnum.RANK.value)
            total_xp = d_row.get(ClanMemberFieldsEnum.TOTAL_XP.value)
            last_rank_date = d_row.get(ClanMemberFieldsEnum.LAST_RANK_DATE.value)

            clan_member = ClanMember(member, joined_date)
            clan_member.rank = rank
            clan_member.total_xp = total_xp
            clan_member.last_rank_date = last_rank_date

            return clan_member
        
        rows_dict = self.df_db.dump(filter_expr)
        return [convert_dict_to_ClanMember(row) for row in rows_dict]
