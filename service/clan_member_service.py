
from datetime import datetime
from typing import List, Optional

from dao import ClanMemberDFDAO
from entity import ClanMember, ClanMemberRankEnum

class ClanMemberService:
    
    def __init__(self, db):
        self._clan_member_dao = ClanMemberDFDAO(db)

    def add_member(self,
                   name: str,
                   joined_date: Optional[int] = None,
                   rank: Optional[ClanMemberRankEnum] = None,
                   total_xp: Optional[int] = None) -> bool:
        clan_member = ClanMember(name, joined_date)
        clan_member.rank = rank or ClanMemberRankEnum.RANK_1.value
        clan_member.last_rank_date = datetime.now().toordinal()
        clan_member.total_xp = total_xp
        return self._clan_member_dao.add(clan_member)

    def update_member(self,
                      name: str,
                      joined_date: Optional[int] = None,
                      rank: Optional[ClanMemberRankEnum] = None,
                      total_xp: Optional[int] = None) -> bool:
        
        clan_member = self.get_member(name)
        if clan_member is None:
            return False
        
        if joined_date:
            clan_member.joined_date = joined_date
        if rank:
            clan_member.rank = rank
            clan_member.last_rank_date = datetime.now().toordinal()
        if total_xp:
            clan_member.total_xp = total_xp
        
        return self._clan_member_dao.update(clan_member)
        
    def delete_member(self, name: str) -> bool:
        clan_member = self.get_member(name)
        if clan_member is None:
            return False
        
        return self._clan_member_dao.delete(clan_member)

    def get_member(self, name: str) -> Optional[ClanMember]:
        return self._clan_member_dao.get(name)

    def get_members(self, filter_expr='') -> List[ClanMember]:
        return self._clan_member_dao.get_all(filter_expr)
