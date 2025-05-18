
from datetime import datetime

from .ientity import IEntity
from .rank import ClanMemberRankEnum

# from entity import IEntity, ClanMemberRankEnum


class ClanMember(IEntity):
    """Clan Member entity class"""

    def __init__(self, member:str, joined_date:datetime):
        self._member : str                  = member
        self._joined_date : datetime        = joined_date

        self._rank : ClanMemberRankEnum     = ClanMemberRankEnum.RANK_INVALID
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
