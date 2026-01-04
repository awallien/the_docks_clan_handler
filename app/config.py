import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

env = os.getenv("ENV", "development")
env_file = f".env.{env}"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_file, extra="ignore")

    DISCORD_TOKEN: str
    ALLOWED_ROLE: str
    BOT_OWNER: str

    DISCORD_GUILD: str
    GENERAL_CHANNEL: str
    FORUM_CHANNEL: str
    VOICE_CHANNEL: str
    DEV_CHANNEL: str
    WELCOME_CHANNEL: str

    DROPS_WEBHOOK: str
    DROPS_CHANNEL: str
    CLUE_THREAD: str
    CLOG_THREAD: str

    ENV: str

    def dev_env(self):
        return self.ENV == "development"

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
