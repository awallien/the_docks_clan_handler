from typing import Optional, List
from datetime import datetime

from dao import IDao
from db import DatabaseColumn, DatabaseRow, DataFrameDatabase, IDatabaseColumns
from entity import ClanMember, ClanMemberRank


class ClanMemberFields(IDatabaseColumns):
    MEMBER = DatabaseColumn("member", "N/A", 'string')
    JOIN_DATE = DatabaseColumn("joined_date", datetime.min.toordinal(), 'Int64')
    RANK = DatabaseColumn("rank", ClanMemberRank.RANK_INVALID, "category", categories=ClanMemberRank.values())
    TOTAL_XP = DatabaseColumn("total_xp", -1, "Int64")
    LAST_RANK_DATE = DatabaseColumn("last_rank_date", datetime.min.toordinal(), "Int64")
    
    @classmethod
    def primary(cls):
        return (cls.MEMBER,)
    
    @staticmethod
    def primary_sort(value):
        return value.str.lower()


class ClanMemberDFDAO(IDao):
    """Clan Member DAO Impl for DataFrame Database"""

    def __init__(self, df_db):
        self._df_db: DataFrameDatabase = df_db

    def add(self, obj: ClanMember) -> bool:
        """Add new clan member to DF Database"""
        db_row = DatabaseRow()

        db_row.put(ClanMemberFields.MEMBER, obj.member)
        db_row.put(ClanMemberFields.JOIN_DATE, obj.joined_date)
        db_row.put(ClanMemberFields.RANK, obj.rank)
        db_row.put(ClanMemberFields.TOTAL_XP, obj.total_xp)
        db_row.put(ClanMemberFields.LAST_RANK_DATE, obj.last_rank_date)

        return self._df_db.add_row(db_row)

    def get(self, member: str) -> Optional[ClanMember]:
        """Get clan member from DF Database"""
        
        prepped_row = DatabaseRow()
        prepped_row.put(ClanMemberFields.MEMBER, member)

        contents = self._df_db.get_row(prepped_row)
        if contents is None:
            return None
        
        member = contents.get(ClanMemberFields.MEMBER)
        joined_date = contents.get(ClanMemberFields.JOIN_DATE)
        rank = contents.get(ClanMemberFields.RANK)
        total_xp = contents.get(ClanMemberFields.TOTAL_XP)
        last_rank_date = contents.get(ClanMemberFields.LAST_RANK_DATE)

        clan_member = ClanMember(member, joined_date)
        clan_member.rank = rank
        clan_member.total_xp = total_xp
        clan_member.last_rank_date = last_rank_date

        return clan_member

    def update(self, obj: ClanMember) -> bool:
        """Update clan member info in DF Database"""
        db_row = DatabaseRow()

        db_row.put(ClanMemberFields.MEMBER, obj.member)
        db_row.put(ClanMemberFields.JOIN_DATE, obj.joined_date)
        db_row.put(ClanMemberFields.RANK, obj.rank)
        db_row.put(ClanMemberFields.TOTAL_XP, obj.total_xp)
        db_row.put(ClanMemberFields.LAST_RANK_DATE, obj.last_rank_date)

        return self._df_db.update_row(db_row)

    def delete(self, obj: ClanMember) -> bool:
        """Delete clan member from DF Database"""
        db_row = DatabaseRow()
        db_row.put(ClanMemberFields.MEMBER, obj.member)
        return self._df_db.delete_row(db_row)

    def get_all(self, filter_expr: str='') -> List[ClanMember]:
        """Get full list of clan members in DF Database"""

        def convert_dict_to_ClanMember(d_row):
            member = d_row.get(ClanMemberFields.MEMBER)
            joined_date = d_row.get(ClanMemberFields.JOIN_DATE)
            rank = d_row.get(ClanMemberFields.RANK)
            total_xp = d_row.get(ClanMemberFields.TOTAL_XP)
            last_rank_date = d_row.get(ClanMemberFields.LAST_RANK_DATE)

            clan_member = ClanMember(member, joined_date)
            clan_member.rank = rank
            clan_member.total_xp = total_xp
            clan_member.last_rank_date = last_rank_date

            return clan_member
        
        rows_dict = self._df_db.dump(filter_expr)
        return [convert_dict_to_ClanMember(row) for row in rows_dict]
