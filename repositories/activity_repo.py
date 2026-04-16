from .base.named_repo import NamedRepository


class ActivityRepository(NamedRepository):
    def __init__(self, db):
        super().__init__(db, "activities")
