from .base_repo import BaseRepository


class ClanMetricRepository(BaseRepository):
    def __init__(self, db, table, id_column):
        super().__init__(db)
        self.table = table
        self.id_column = id_column

    def upsert_value(self, clan_id, ref_id, value_column, value):
        self.execute(f"""
            INSERT INTO {self.table} (clan_id, {self.id_column}, {value_column})
            VALUES (?, ?, ?)
            ON CONFLICT(clan_id, {self.id_column})
            DO UPDATE SET {value_column} = excluded.{value_column}
        """, (clan_id, ref_id, value))

    def increment_value(self, clan_id, ref_id, value_column, amount):
        self.execute(f"""
            INSERT INTO {self.table} (clan_id, {self.id_column}, {value_column})
            VALUES (?, ?, ?)
            ON CONFLICT(clan_id, {self.id_column})
            DO UPDATE SET {value_column} = {value_column} + ?
        """, (clan_id, ref_id, amount, amount))
