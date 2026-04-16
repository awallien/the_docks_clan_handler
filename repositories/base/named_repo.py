from .base_repo import BaseRepository


class NamedRepository(BaseRepository):
    def __init__(self, db, table_name):
        super().__init__(db)
        self.table = table_name

    def create(self, name):
        return self.execute(
            f"INSERT INTO {self.table} (name) VALUES (?)",
            (name,)
        ).lastrowid

    def get_by_name(self, name):
        return self.fetch_one(
            f"SELECT * FROM {self.table} WHERE name = ?",
            (name,)
        )

    def list_all(self):
        return self.fetch_all(
            f"SELECT * FROM {self.table}"
        )
