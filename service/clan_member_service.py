
from datetime import datetime
from typing import List, Optional

from dao import ClanMemberDFDAO
from entity import ClanMember, ClanMemberRankEnum

class ClanMemberService:
    
    def __init__(self):
        self._clan_member_dao = ClanMemberDFDAO()

    def get_db(self):
        return self._clan_member_dao.db
    
    def set_db(self, df_db):
        """Set the DataFrame Database instance"""
        self._clan_member_dao.db = df_db
        return True

    def add_member(self, name: str, joined_date: datetime):
        clan_member = ClanMember(name, joined_date)
        return self._clan_member_dao.add(clan_member)

    def update_member(self,
                      name: str,
                      joined_date: Optional[datetime] = None,
                      rank: Optional[ClanMemberRankEnum] = None,
                      total_xp: Optional[int] = None) -> bool:
        
        clan_member = self.get_member(name)
        if clan_member is None:
            return False
        
        if joined_date:
            clan_member.joined_date = joined_date
        if rank:
            clan_member.rank = rank
            clan_member.last_rank_date = datetime.now()
        if total_xp:
            clan_member.total_xp = total_xp
        
        return self._clan_member_dao.update(clan_member)
        
    def delete_member(self, name: str) -> bool:
        clan_member = self.get_member(name)
        if clan_member is None:
            return False
        
        return self._clan_member_dao.delete(name)

    def get_member(self, name: str) -> Optional[ClanMember]:
        return self._clan_member_dao.get(name)

    def get_members(self, filter_expr='') -> List[ClanMember]:
        return self._clan_member_dao.get_all(filter_expr)
