from .base.named_repo import NamedRepository


class BossRepository(NamedRepository):
    def __init__(self, db):
        super().__init__(db, "bosses")
