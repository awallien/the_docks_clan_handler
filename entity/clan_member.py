
from .ientity import IEntity
from .rank import ClanMemberRank


class ClanMember(IEntity):
    """Clan Member entity class"""

    def __init__(self, member:str, joined_date:int = 0):
        self._member : str                  = member
        self._joined_date : int             = joined_date

        self._rank : ClanMemberRank         = ClanMemberRank.RANK_INVALID

    @property
    def member(self):
        return self._member
    
    @property
    def rank(self):
        return self._rank
    
    @property
    def joined_date(self):
        return self._joined_date
    
    @member.setter
    def member(self, value):
        self._member = value
    
    @rank.setter
    def rank(self, value):
        self._rank = value
    
    @joined_date.setter
    def joined_date(self, value):
        self._joined_date = value
    
    def __str__(self):
        return f"ClanMember({self.member}, {self.joined_date}, {self.rank})"
    
    def __repr__(self):
        return str(self)
