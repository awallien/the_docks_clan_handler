
from datetime import datetime
from service import ClanMemberService

class DocksClanCallback:

    def __init__(self):
        self._clan_member_service = ClanMemberService()

    def _convert_to_datetime(date_str: str, date_format: str="%Y-%m-%d") -> datetime:
        """Convert date string to datetime object"""
        try:
            date_obj = datetime.strptime(date_str, date_format)
            return date_obj
        except:
            return False    
