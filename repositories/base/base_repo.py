from db import Database

class BaseRepository:
    def __init__(self, db):
        self.db: Database = db

    def fetch_one(self, query, params=()):
        return self.db.fetch_one(query, params)

    def fetch_all(self, query, params=()):
        return self.db.fetch_all(query, params)

    def execute(self, query, params=()):
        return self.db.execute(query, params)
