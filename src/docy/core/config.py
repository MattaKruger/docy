from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    GITHUB_ACCESS_TOKEN: str = Field(default="")
    GROQ_API_KEY: str = Field(default="")
    OBSIDIAN_VAULT_DIR: str = Field(default="")
    GEMINI_API_KEY: str = Field(default="")
    GOOGLE_API_KEY: str = Field(default="")

    DB_HOST: str = Field(default="")
    DB_USER: str = Field(default="")
    DB_PASS: str = Field(default="")
    DB_NAME: str = Field(default="")
    DB_PORT: str = Field(default="5432")

    TEST_DB_NAME: str = Field(default="")
    DOCY_DATA_DIR: str = Field(default="")
