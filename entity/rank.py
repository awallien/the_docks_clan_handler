

from enum import UNIQUE, StrEnum, verify
from typing import List, Self


@verify(UNIQUE)
class ClanMemberRankEnum(StrEnum):
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
    def members(cls) -> List[Self]:
        return list(cls)
    
    @classmethod
    def values(cls) -> List[str]:
        return list(member.value for member in cls)

    @classmethod
    def activeness_ranks(cls) -> List[Self]:
        return cls.members[1:5]
    
    @classmethod
    def achievement_ranks(cls) -> List[Self]:
        return cls.members[5:16]
    
    @classmethod
    def honorable_ranks_non_challenged(cls) -> List[Self]:
        return cls.members[16:21]
    
    @classmethod
    def honorable_ranks_challenged(cls) -> List[Self]:
        return cls.members[22:25]
    
    @classmethod
    def administrative_ranks(cls) -> List[Self]:
        return cls.members[26:29]

    # @classmethod
    # def get_next_rank(cls, current_rank: Self) -> Self:
    #     ranks = list(cls)
    #     ranks_len = len(ranks)
    #     for ix, rank in enumerate(ranks):
    #         if rank.value == current_rank.value:
    #             return ranks[min(ranks_len-1, ix+1)]
    #     assert ValueError(f"Unable to retrieve next rank from current rank {str(current_rank)}")
