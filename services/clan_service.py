from typing import List


class ClanService:
    def __init__(self, clan_repo):
        self.clan_repo = clan_repo

    def create_member(self, name, joined_date=None, rank=None):
        if not name or len(name) < 2:
            raise ValueError("Invalid name")

        if self.clan_repo.get_by_name(name):
            raise ValueError("Member already exists")

        return self.clan_repo.create(name, joined_date, rank)

    def get_member(self, name):
        member = self.clan_repo.get_by_name(name)
        if not member:
            raise ValueError("Member not found")
        return member
    
    def get_members(self, mambers: List[str]):
        members = self.clan_repo.get_members(members)
        return members

    def list_members(self):
        return self.clan_repo.list_all()

    def delete_member(self, name):
        member = self.get_member(name)
        self.clan_repo.delete(member["id"])

    def delete_members(self, members: List[str]):
        return self.clan_repo.delete_members(members)