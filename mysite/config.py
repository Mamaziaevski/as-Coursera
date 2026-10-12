from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///" + (PROJECT_DIR / "users.db").as_posix()
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    SECRET_KEY: str = ""
    OLLAMA_URL: str = "http://127.0.0.1:11434"
    OLLAMA_MODEL: str = "llama3.2:latest"
    EMBEDDING_MODEL: str = "qwen3-embedding:0.6b"

    model_config = SettingsConfigDict(
        env_file=PROJECT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
if len(settings.SECRET_KEY) < 32:
    raise ValueError("Задай SECRET_KEY в .env и задай SECRET_KEY длиной от 32 символов")
if not settings.DATABASE_URL.startswith(("sqlite:///", "sqlite+aiosqlite:///")):
    raise ValueError("Этот учебный черновик использует SQLite")
