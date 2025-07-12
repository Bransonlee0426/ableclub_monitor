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
    EMAIL_DEBUG_MODE: bool = Field(default=True, description="Email 除錯模式，啟用時只輸出到 console")
    EMAIL_USER: str = Field(default="", description="SMTP 用戶名")
    EMAIL_PASSWORD: str = Field(default="", description="SMTP 密碼或應用程式密碼")
    DEFAULT_NOTIFICATION_EMAIL: str = Field(default="", description="預設通知接收 Email")
    
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


    model_config = ConfigDict(
        # The name of the file to load environment variables from.
        env_file=".env"
    )

# Create a single, reusable instance of the settings.
settings = Settings()
