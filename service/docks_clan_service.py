from datetime import datetime
from db_repo import ClanRankRepo
from typing import List


class DocksClanService:

    def __init__(self, clan_rank_repo: ClanRankRepo):
        self._clan_rank_repo = clan_rank_repo

    def create_member(self,
                      member: str,
                      joined_date: datetime):
        ...

    def list_members(self,
                     members: List[str] = None):
        ...

    def update_members(self,
                       choice: str = "rank"):
        ...

    def delete_members(self,
                       members: List[str]):
        ...


    

    
