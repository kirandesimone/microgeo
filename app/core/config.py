"""Application configuration"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Runtime configuration for the Geocode Location Service"""

    app_name: str = "Geocode Location Service"
    app_version: str = "0.1.0"

    host: str = "127.0.0.1"
    port: int = 8000

    # APIs
    overpass_url: str = "https://overpass-api.de/api/interpreter"
    nominatim_url: str = "https://nominatim.openstreetmap.org"

    # Required User-Agent header
    @property
    def user_agent(self) -> str:
        """Construct the user agent string."""
        return f"microgeo-service/{self.app_version} (internal-dev)"

    # Performance budget for User Story #1 (< 3s under normal load)
    area_query_budget_seconds: float = 3.0
    # Default timeout for general HTTP requests
    request_timeout_seconds: float = 10.0
    max_retries: int = 3


def get_settings() -> Settings:
    """Cached settings accessor. Use this as a FastAPI dependency."""
    return Settings()
