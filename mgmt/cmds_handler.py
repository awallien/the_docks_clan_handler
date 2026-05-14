from typing import List, Any, Dict, Set
from datetime import datetime

from container import Container
from entity import ClanMemberRank

class CommandSpecsArgsException(Exception):
    pass


class CommandSpecsHandler:

    def __init__(self, container: Container):
        self._container = container
        self._clan_service = container.clan_service()
    
    @staticmethod
    def _parse_kv_tokens(tokens: List[str]) -> Dict[str, Any]:
        """Parse key=value tokens into payload"""
        payload: Dict[str, Any] = {}
        for token in tokens:
            if "=" not in token:
                raise CommandSpecsArgsException(f"Expected key=value token, got '{token}'")
            key, value = token.split("=", 1)
            key = key.strip()
            value = value.strip()
            if not key or value == "":
                raise CommandSpecsArgsException(f"Invalid key=value token '{token}'")
            payload[key] = value
        return payload

    @staticmethod
    def _check_missing_args(required_args: Set, payload: Dict):
        missing_args = required_args - payload.keys()
        if missing_args:
            raise CommandSpecsArgsException(f"Missing required arguments: {missing_args}")

    @staticmethod
    def _dt_to_ordinal(date: str):
        return datetime.fromisoformat(date).toordinal()

    @staticmethod
    def _ordinal_to_dt(ordinal: int):
        return datetime.fromordinal(int(ordinal)).strftime("%Y-%m-%d")

    def cmd_cm(self, tokens: List[str], **args):
        """Ex: /cm member=new_member joined_date=2021-01-01 rank=1"""
        required_args = {"member", "joined_date"}
        payload = self._parse_kv_tokens(tokens)

        self._check_missing_args(required_args, payload)

        member = payload["member"]
        joined_date = self._dt_to_ordinal(payload["joined_date"])
        
        rank = payload.get("rank", ClanMemberRank.RANK_1)

        last_row_id = self._clan_service.create_member(
            name = member,
            joined_date = joined_date,
            rank = rank,
        )

        return f"Created member {member} with id {last_row_id}"

    def cmd_rm(self, tokens: List[str], **args):
        """Ex: /rm [member1 member2]"""

        members = []
        if not len(tokens):
            members = self._clan_service.list_members()
        else:
            members = self._clan_service.get_members(tokens)    

        if not members:
            raise CommandSpecsArgsException("Unable to find any members.")

        return [dict(member) for member in members] 


    def cmd_um(self, tokens: List[str], **args):
        """Ex: /um member=member1 ..."""
        required_args = {"member"}
        payload = self._parse_kv_tokens(tokens)

        self._check_missing_args(required_args, payload)

        member = payload.pop("member")
        if not payload:
            raise CommandSpecsArgsException(f"No values to update for member {member}")

        for date_field in {"joined_date", "last_rank_date"} & payload.keys():
            payload[date_field] = self._dt_to_ordinal(payload[date_field])

        updated = self._clan_service.update_member(member, payload)
        return f"Updated {updated} member(s)"


    def cmd_dm(self, tokens: List[str], **args):
        """Ex: /dm member1 ..."""
        members = tokens
        if not members:
            raise CommandSpecsArgsException("No members to delete.")

        if len(members) == 1:
            return self._clan_service.delete_member(members[0])
        else:
            return self._clan_service.delete_members(members)
        