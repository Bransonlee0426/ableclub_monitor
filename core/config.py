# /core/config.py

from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict

class Settings(BaseSettings):
    """
    Manages application settings using Pydantic.
    Reads environment variables from a .env file.
    """
    DATABASE_URL: str = Field(default="sqlite:///./ableclub_monitor.db", description="Database connection URL")
    
    # --- Email 通知設定 ---
    EMAIL_DEBUG_MODE: bool = False  # 強制設定
    EMAIL_USER: str = "anythingforgood@gmail.com"  # 強制設定
    EMAIL_PASSWORD: str = "rukmfywwollcoyfx"  # 強制設定
    DEFAULT_NOTIFICATION_EMAIL: str = "xebiva9350@axcradio.com"  # 強制設定
    
    # --- Telegram 通知設定 ---
    TELEGRAM_BOT_TOKEN: str = Field(default="", description="Telegram Bot Token")
    TELEGRAM_CHAT_ID: str = Field(default="", description="Telegram Chat ID")

    # --- JWT (Authentication) Settings ---
    # A strong, secret key for signing the JWT.
    # In production, this should be loaded from the environment and be a long, random string.
    SECRET_KEY: str = Field(default="a_very_secret_key_that_should_be_changed", description="Secret key for signing JWTs")
    # The algorithm to use for JWT signing.
    ALGORITHM: str = "HS256"
    # The expiration time for access tokens in minutes.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 days (30 * 24 * 60)
    
    # --- CORS and Environment Settings ---
    ENABLE_CORS: bool = Field(default=False, description="Enable CORS middleware")
    LOG_LEVEL: str = Field(default="INFO", description="Application log level")
    ENVIRONMENT: str = Field(default="local", description="Application environment (local, dev, prod)")
    
    # --- Job Scheduler Settings ---
    SCHEDULER_ENABLED: bool = Field(default=False, description="Enable job scheduler")
    SCHEDULER_TIMEZONE: str = Field(default="Asia/Taipei", description="Scheduler timezone")
    SCRAPER_JOB_INTERVAL_HOURS: int = Field(default=1, description="Scraper job interval in hours")
    NOTIFICATION_JOB_INTERVAL_HOURS: int = Field(default=1, description="Notification job interval in hours")
    JOB_MAX_INSTANCES: int = Field(default=1, description="Maximum job instances")
    JOB_RETRY_MAX: int = Field(default=3, description="Maximum job retry attempts")


    model_config = ConfigDict(
        # The name of the file to load environment variables from.
        env_file=".env",
        env_file_encoding="utf-8"
    )

# Create a single, reusable instance of the settings.
settings = Settings()
