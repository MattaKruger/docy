from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    BASE_URL: str = Field(default="http://localhost:8000")

    DB_HOST: str = Field(default="")
    DB_USER: str = Field(default="")
    DB_PASS: str = Field(default="")
    DB_NAME: str = Field(default="")
    DB_PORT: str = Field(default="5432")
