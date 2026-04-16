from .base.named_repo import NamedRepository


class SkillRepository(NamedRepository):
    def __init__(self, db):
        super().__init__(db, "skills")
