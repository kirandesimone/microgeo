"""
Client for Nominatim API.
"""

import logging
from typing import Any
import httpx

from app.core.config import Settings

logger = logging.getLogger(__name__)


class NominatimClient:
    """
    Async wrapper around Nominatim API.
    """

    def __init__(self, settings: Settings, http_client: httpx.AsyncClient):
        self._settings = settings
        self._http = http_client

        # Check user agent valid
        if not self._settings.user_agent:
            raise ValueError("A valid User-Agent is required.")
