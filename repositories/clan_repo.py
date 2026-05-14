from typing import NotRequired, TypedDict

from db import Database

class ClanUpdateValues(TypedDict, total=False):
    member: NotRequired[str]
    joined_date: NotRequired[int]
    rank: NotRequired[str]
    last_rank_date: NotRequired[int]

class ClanRepository:
    def __init__(self, db: Database):
        self.db: Database = db

    @staticmethod
    def _row_to_dict(row):
        return dict(row) if row is not None else None

    def create(self, member, joined_date=None, rank=None):
        result = self.db.execute(
            "INSERT INTO clan (member, joined_date, rank) VALUES (?, ?, ?)",
            (member, joined_date, rank)
        )
        return result.lastrowid

    def get_by_id(self, clan_id):
        return self._row_to_dict(self.db.fetch_one(
            "SELECT * FROM clan WHERE id = ?",
            (clan_id,)
        ))

    def get_by_name(self, member):
        return self._row_to_dict(self.db.fetch_one(
            "SELECT * FROM clan WHERE member = ?",
            (member,)
        ))
    
    def get_members(self, members):
        placeholders = ",".join("?" for _ in members)
        query = f"SELECT * FROM clan WHERE member IN ({placeholders})"
        return list(self.db.fetch_all(query, members))

    def list_all(self):
        return list(self.db.fetch_all("SELECT * FROM clan"))
    
    def update_by_name(self, member: str, values: ClanUpdateValues) -> int:
        allowed_fields = set(ClanUpdateValues.__annotations__)
        unknown_fields = set(values) - allowed_fields

        if unknown_fields:
            raise ValueError(f"Unsupported clan fields: {sorted(unknown_fields)}")
        
        if not values:
            return 0
        
        assignments = ", ".join(f"{field} = ?" for field in values)
        params = tuple(values.values()) + (member, )
        result = self.db.execute(
            f"UPDATE clan SET {assignments} where MEMBER = ?",
            params,
        )
        return result.rowcount

    def delete_members(self, members):
        placeholders = ",".join("?" for _ in members)
        query = f"DELETE FROM clan WHERE member IN ({placeholders})"
        result = self.db.execute(query, members)
        return result.rowcount

    def delete(self, clan_id):
        result = self.db.execute("DELETE FROM clan WHERE id = ?", (clan_id,))
        return result.rowcount