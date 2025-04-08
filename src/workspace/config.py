import pathlib

from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

DRIVE_ROOT_DIR = pathlib.Path(__file__).parent.resolve()


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    BASE_DATA_DIR: pathlib.Path = Field(default=DRIVE_ROOT_DIR / "data")
    CODING_SUBDIR: str = "coding"

    API_BASE_URL: str = Field(default="http://localhost:8000")
    API_TASK_URL: str = Field(default=f"{API_BASE_URL}/tasks/")
    DB_HOST: str = Field(default="")
    DB_USER: str = Field(default="")
    DB_PASS: str = Field(default="")
    DB_NAME: str = Field(default="")
    DB_PORT: str = Field(default="5432")

    OLLAMA_BASE_URL: HttpUrl = Field(default=HttpUrl("http://localhost:11434/v1"))
    OLLAMA_MODEL: str = Field(default="gemma3:12b")  # Make model names configurable
    GEMINI_MODEL: str = Field(default="gemini-2.0-pro-exp-02-05")
    GEMINI_PROVIDER: str = Field(default="google-gla")  # Check if provider needs API key env var
    GROQ_MODEL: str = Field(default="meta-llama/llama-4-scout-17b-16e-instruct")

    DEFAULT_MAX_TOKENS: int = 1024
    DEFAULT_TEMPERATURE: float = 0.5


settings = Config()
