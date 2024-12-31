from datetime import datetime
from enum import Enum, verify, UNIQUE

@verify(UNIQUE)
class ClanMemberDAOFields(Enum):
    MEMBER = "Member"
    JOINED_DATE = "Joined Date"
    RANK = "Rank"
    TOTAL_XP = "Total XP"
    LAST_RANK_DATE = "Last Rank Date"

    @classmethod
    def as_list(cls):
        return list(cls.__members__.keys())


class ClanMemberDAO:
    def __init__(self, member, joined_date):
        self._member : str = member
        self._joined_date : datetime = joined_date

        self._rank : str = ""
        self._total_xp : int = -1
        self._last_ranked_date : datetime = datetime.min

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
    def last_ranked_date(self):
        return self._last_ranked_date
    
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

    @last_ranked_date.setter
    def last_ranked_date(self, value):
        if not isinstance(value, datetime):
            raise TypeError("ClanMember:last_ranked_date:value is not a datetime:", value)
        self._last_ranked_date = value