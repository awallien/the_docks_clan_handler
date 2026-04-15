from db import Database
from datetime import datetime
from typing import Any, Dict, List, Set

class ClanRankRepo:
    def __init__(self, db):
        self._db: Database = db

    def get(self,
            prim_key: str):
        ...

    def insert(self, 
               values: Dict[str, Any]):
        ...

    def update(self, 
               values: Dict[str, Any]):
        ...

    def delete(self,
               values: Dict[str, Any]):
        ...

    def create_member(self,
                      member: str,
                      joined_date: datetime):
        ...