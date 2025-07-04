from datetime import datetime
from typing import Optional, List

from dao import IDao
from db import DatabaseColumn, DatabaseRow, DataFrameDatabase, IDatabaseColumns
from entity import ClanMember, ClanMemberRankEnum


class ClanMemberFields(IDatabaseColumns):
    MEMBER = DatabaseColumn("Member", "N/A", "string")
    JOIN_DATE = DatabaseColumn("Join_Date", datetime.min, "datetime64[ns]")
    RANK = DatabaseColumn("Rank", ClanMemberRankEnum.RANK_INVALID.value, "category", categories=ClanMemberRankEnum.values())
    TOTAL_XP = DatabaseColumn("Total_XP", -1, "int64")
    LAST_RANK_DATE = DatabaseColumn("Last_Rank_Date", datetime.min, "datetime64[ns]")

    @classmethod
    def members(cls):
        return list(cls.__members__.keys())
    
    @classmethod
    def values(cls):
        return [field.value for field in cls]
    
    @classmethod
    def primary(cls):
        return (cls.MEMBER.value,)
    
    @staticmethod
    def primary_sort(col):
        return col.str.lower()


class ClanMemberDFDAO(IDao):
    """Clan Member DAO Impl for DataFrame Database"""

    def __init__(self):
        self._cols = ClanMemberFields.values()
        self._prim_cols = ClanMemberFields.primary()
        self._prim_sort_fn = ClanMemberFields.primary_sort
        self._df_db = self.__init_db()

    def __init_db(self) -> None:
        self._df_db = DataFrameDatabase(prim_cols=self._prim_cols, 
                                        cols=self._cols,
                                        prim_cols_sort_fn=self._prim_sort_fn)

    @property
    def db(self) -> DataFrameDatabase:
        """Get DataFrame Database instance"""
        return self._df_db

    def add(self, obj: ClanMember) -> bool:
        """Add new clan member to DF Database"""
        db_row = DatabaseRow()

        db_row.put(ClanMemberFields.MEMBER.value, obj.member)
        db_row.put(ClanMemberFields.JOIN_DATE.value, obj.joined_date)
        db_row.put(ClanMemberFields.RANK.value, obj.rank)
        db_row.put(ClanMemberFields.TOTAL_XP.value, obj.total_xp)
        db_row.put(ClanMemberFields.LAST_RANK_DATE.value, obj.last_rank_date)

        return self._df_db.add_row(db_row)

    def get(self, key: str) -> Optional[ClanMember]:
        """Get clan member from DF Database"""
        contents = self._df_db.get_row(key)
        if contents is None:
            return None
        
        member = contents.get(ClanMemberFields.MEMBER.value)
        joined_date = contents.get(ClanMemberFields.JOIN_DATE.value)
        rank = contents.get(ClanMemberFields.RANK.value)
        total_xp = contents.get(ClanMemberFields.TOTAL_XP.value)
        last_rank_date = contents.get(ClanMemberFields.LAST_RANK_DATE.value)

        clan_member = ClanMember(member, joined_date)
        clan_member.rank = rank
        clan_member.total_xp = total_xp
        clan_member.last_rank_date = last_rank_date

        return clan_member

    def update(self, obj: ClanMember) -> bool:
        """Update clan member info in DF Database"""
        db_row = DatabaseRow()

        db_row.put(ClanMemberFields.MEMBER.value, obj.member)
        db_row.put(ClanMemberFields.JOIN_DATE.value, obj.joined_date)
        db_row.put(ClanMemberFields.RANK.value, obj.rank)
        db_row.put(ClanMemberFields.TOTAL_XP.value, obj.total_xp)
        db_row.put(ClanMemberFields.LAST_RANK_DATE.value, obj.last_rank_date)

        return self._df_db.update_row(db_row)

    def delete(self, obj: ClanMember) -> bool:
        """Delete clan member from DF Database"""
        db_row = DatabaseRow()

        db_row.put(ClanMemberFields.MEMBER, obj.member)

        return self._df_db.delete_row(db_row)

    def get_all(self, filter_expr: str='') -> List[ClanMember]:
        """Get full list of clan members in DF Database"""

        def convert_dict_to_ClanMember(d_row):
            member = d_row.get(ClanMemberFields.MEMBER.value)
            joined_date = d_row.get(ClanMemberFields.JOIN_DATE.value)
            rank = d_row.get(ClanMemberFields.RANK.value)
            total_xp = d_row.get(ClanMemberFields.TOTAL_XP.value)
            last_rank_date = d_row.get(ClanMemberFields.LAST_RANK_DATE.value)

            clan_member = ClanMember(member, joined_date)
            clan_member.rank = rank
            clan_member.total_xp = total_xp
            clan_member.last_rank_date = last_rank_date

            return clan_member
        
        rows_dict = self._df_db.dump(filter_expr)
        return [convert_dict_to_ClanMember(row) for row in rows_dict]
