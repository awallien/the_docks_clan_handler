from db import Database


class ClanRepository:
    def __init__(self, db: Database):
        self.db: Database = db

    def create(self, member, joined_date=None, rank=None):
        cursor = dict(self.db.execute(
            "INSERT INTO clan (member, joined_date, rank) VALUES (?, ?, ?)",
            (member, joined_date, rank)
        ))
        return cursor.lastrowid

    def get_by_id(self, clan_id):
        return dict(self.db.fetch_one(
            "SELECT * FROM clan WHERE id = ?",
            (clan_id,)
        ))

    def get_by_name(self, member):
        return dict(self.db.fetch_one(
            "SELECT * FROM clan WHERE member = ?",
            (member,)
        ))
    
    def get_members(self, members):
        placeholders = ",".join("?" for _ in members)
        query = f"SELECT * FROM clan WHERE member IN ({placeholders})"
        return list(self.db.fetch_all(query, members))

    def list_all(self):
        return list(self.db.fetch_all("SELECT * FROM clan"))

    def delete_members(self, members):
        placeholders = ",".join("?" for _ in members)
        query = f"DELETE FROM clan WHERE member IN ({placeholders})"
        exec = self.db.execute(query, members)
        return exec.rowcount

    def delete(self, clan_id):
        exec = self.db.execute("DELETE FROM clan WHERE id = ?", (clan_id,))
        return exec.rowcount