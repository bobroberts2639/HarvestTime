"""Harvest Time — Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "Harvest Time"
    app_version: str = "0.1.0"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/harvest_time"
    database_echo: bool = False

    # Redis (for Celery task queue)
    redis_url: str = "redis://localhost:6379/0"

    # JWT Authentication
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # Weather API
    open_meteo_base_url: str = "https://api.open-meteo.com/v1"
    visual_crossing_api_key: str = ""

    # SMS (Twilio)
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_number: str = ""

    # Push notifications (Firebase)
    firebase_credentials_path: str = ""

    # CORS
    allowed_origins: list[str] = ["http://localhost:3000"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
