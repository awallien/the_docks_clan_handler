# repositories/clan_repo.py
class ClanRepository:
    def __init__(self, db):
        self.db = db

    def create(self, member, joined_date=None, rank=None):
        cursor = self.db.execute(
            "INSERT INTO clan (member, joined_date, rank) VALUES (?, ?, ?)",
            (member, joined_date, rank)
        )
        return cursor.lastrowid

    def get_by_id(self, clan_id):
        return self.db.fetch_one(
            "SELECT * FROM clan WHERE id = ?",
            (clan_id,)
        )

    def get_by_name(self, member):
        return self.db.fetch_one(
            "SELECT * FROM clan WHERE member = ?",
            (member,)
        )

    def list_all(self):
        return self.db.fetch_all("SELECT * FROM clan")

    def delete(self, clan_id):
        self.db.execute("DELETE FROM clan WHERE id = ?", (clan_id,))