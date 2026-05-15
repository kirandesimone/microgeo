"""Application configuration"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Runtime configuration for the Geocode Location Service"""

    app_name: str = "Geocode Location Service"
    app_version: str = "0.1.0"

    host: str = "127.0.0.1"
    port: int = 8000

    overpass_url: str = "https://overpass-api.de/api/interpreter"

    # performance budget for User Story #1 (< 3s under normal load)
    area_query_budget_seconds: float = 3.0

    # Default timeout for general HTTP requests
    request_timeout_seconds: float = 10.0


def get_settings() -> Settings:
    """Cached settings accessor. Use this as a FastAPI dependency."""
    return Settings()
