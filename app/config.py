import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from functools import lru_cache

env = os.getenv("ENV", "development")
env_file = f".env.{env}"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_file, extra="ignore")

    DISCORD_TOKEN: str
    ALLOWED_ROLES: str
    ADMIN_ROLE: str
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
    AGENT_CMD: str
    AGENT_MODEL: str = "gpt-5.3-codex-fast"
    AGENT_API_KEY: str = ""

    @field_validator("ALLOWED_ROLES", "ADMIN_ROLE")
    @classmethod
    def validate_role_names(cls, value: str) -> str:
        if not value.strip() or ("," in value and not all(name.strip() for name in value.split(","))):
            raise ValueError("Role names must not be empty")
        return value.strip()

    @field_validator("ADMIN_ROLE")
    @classmethod
    def validate_admin_role(cls, value: str) -> str:
        if "," in value:
            raise ValueError("ADMIN_ROLE must be a single role name")
        return value

    @property
    def general_command_roles(self) -> tuple[str, ...]:
        roles = [name.strip() for name in self.ALLOWED_ROLES.split(",")]
        return tuple(dict.fromkeys([*roles, self.ADMIN_ROLE]))

    def dev_env(self):
        return self.ENV == "development"

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
