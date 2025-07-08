# /core/config.py

from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """
    Manages application settings using Pydantic.
    Reads environment variables from a .env file.
    """
    DATABASE_URL: str = Field(default="sqlite:///./ableclub_monitor.db", description="Database connection URL")
    LINE_NOTIFY_TOKEN: str = Field(default="", description="LINE Notify API Token")

    # --- New settings for LINE OAuth ---
    # These are added for the LINE Notify OAuth 2.0 flow.
    
    # Channel ID from LINE Developers console.
    LINE_CLIENT_ID: str = "2007708517"
    
    # Channel Secret from LINE Developers console.
    LINE_CLIENT_SECRET: str = "ce564290c76b2def3620823c1b8ff5e3"
    
    # The callback URL that LINE will redirect to after user authorization.
    # For local development, this needs to be a public URL (e.g., using ngrok).
    LINE_REDIRECT_URI: str = "http://localhost:8000/api/line/callback"
    
    # The URL to redirect the user to after a successful authorization.
    FRONTEND_REDIRECT_SUCCESS_URL: str = "http://localhost:8080/line-bind-success"
    
    # The URL to redirect the user to after a failed authorization.
    FRONTEND_REDIRECT_FAILURE_URL: str = "http://localhost:8080/line-bind-failure"
    # --- End of new settings ---

    class Config:
        # The name of the file to load environment variables from.
        env_file = ".env"

# Create a single, reusable instance of the settings.
settings = Settings()