from pydantic import BaseSettings
import os

class Settings(BaseSettings):
    """
    Manages application settings using Pydantic.
    Reads environment variables from a .env file.
    """
    DATABASE_URL: str
    LINE_NOTIFY_TOKEN: str

    class Config:
        # The name of the file to load environment variables from.
        env_file = ".env"

# Create a single, reusable instance of the settings.
settings = Settings()
