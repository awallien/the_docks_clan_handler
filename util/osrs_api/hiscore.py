import requests

if __name__ == "__main__":
    from skills import *
    from activities import *
    from bosses import *
else:
    from util.osrs_api import *

from enum import Enum, verify, UNIQUE
from http import HTTPStatus

HISCORE_API_URL_FMT = "https://secure.runescape.com/m=hiscore_oldschool%s/index_lite.ws?player=%s"

@verify(UNIQUE)
class AccountTypes(Enum):
    NORMAL = ""
    IRONMAN = "_ironman"
    HARDCORE_IRONMAN = "_hardcore_ironman"
    ULTIMATE_IRONMAN = "_ultimate"
    DEADMAN = "_deadman"
    SEASONAL = "_seasonal"
    TOURNAMENT = "_tournament"
    FRESH_START = "_fresh_start"

class Hiscore:
    def __init__(self, username: str, account_type: AccountTypes = None):
        self._username = username
        self._account_type = account_type if account_type else AccountTypes.NORMAL
        
        self._total_xp = -1
        self._total_rank = -1
        self._total_level = -1
        self._activities = Activities()
        self._bosses = Bosses()
        self._skills = Skills()

        self._url = None
        self.__set_url()

        self.__fetch_user_data()

    def __set_url(self):
        self._url = HISCORE_API_URL_FMT % (self.account_type.value, self.username)

    def __parse_user_data(self, content):
        idx = 0
        content_fields = content.strip().split("\n")
        
        self._total_rank, self._total_level, self._total_xp = map(int, content_fields[idx].split(","))
        idx += 1

        for skill in SKILLS:
            skill_cls = self._skills.get(skill)
            skill_cls.rank, skill_cls.level, skill_cls.xp = map(int, content_fields[idx].split(","))
            idx += 1
        
        for activity in ACTIVITIES:
            act_cls = self.activities.get(activity)
            act_cls.rank, act_cls.score = map(int, content_fields[idx].split(","))
            idx += 1

        for boss in BOSSES:
            boss_cls = self.bosses.get(boss)
            boss_cls.rank, boss_cls.score = map(int, content_fields[idx].split(","))
            idx += 1

    def __fetch_user_data(self):
        response = requests.get(url=self._url)
        if response.status_code == HTTPStatus.OK:
            self.__parse_user_data(response.content.decode())
        else:
            raise Exception(f"Unable to find {self.username} in Hiscores")

    @property
    def username(self):
        return self._username
    
    @property
    def account_type(self):
        return self._account_type

    @property
    def total_xp(self):
        return self._total_xp
    
    @property
    def total_rank(self):
        return self._total_rank

    @property
    def total_level(self):
        return self._total_level

    @property
    def activities(self):
        return self._activities
    
    @property
    def bosses(self):
        return self._bosses

    @property
    def skills(self):
        return self._skills
    
    def __str__(self):
        return f"HiScore({self.username}, {self.account_type}, {self.total_rank}, {self.total_level}, {self.total_xp})"
