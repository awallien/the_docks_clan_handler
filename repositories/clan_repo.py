from typing import NotRequired, TypedDict

from db import Database
from .hiscore_repo import utc_now

class ClanUpdateValues(TypedDict, total=False):
    member: NotRequired[str]
    joined_date: NotRequired[int]
    rank: NotRequired[str]

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
        if "rank" in values or ("member" in values and values["member"] != member):
            with self.db.connection() as conn:
                conn.execute("BEGIN IMMEDIATE")
                row = conn.execute("SELECT id, rank FROM clan WHERE member = ?", (member,)).fetchone()
                result = conn.execute(f"UPDATE clan SET {assignments} WHERE member = ?", params)
                if row is not None and "member" in values and values["member"] != member:
                    conn.execute("DELETE FROM hiscore_refresh WHERE clan_id = ?", (row["id"],))
                if row is not None and "rank" in values and values["rank"] != row["rank"]:
                    conn.execute("UPDATE clan SET last_rank_update = NULL WHERE id = ?", (row["id"],))
                    conn.execute("UPDATE rank_changes SET superseded_at = ? WHERE clan_id = ? AND acknowledged_at IS NULL AND superseded_at IS NULL", (utc_now(), row["id"]))
                conn.commit()
                return result.rowcount
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
