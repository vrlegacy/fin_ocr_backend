import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./finch_local.db"
    AUTH0_DOMAIN: str = "dev-f26bdihea4sqt7k4.us.auth0.com"
    AUTH0_AUDIENCE: str = "glTXHJq0MuLfyceaq1hbmjrBY42BgIKD"
    AUTH0_CLIENT_ID: str = ""
    AUTH0_CLIENT_SECRET: str = ""
    GEMINI_API_KEY: str = ""
    ALLOWED_ORIGINS: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
