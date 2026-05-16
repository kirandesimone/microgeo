"""
Client for Nominatim API.
"""

import logging
import httpx
import asyncio
from typing import Any

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

    async def _enforce_rate_limit(self) -> None:
        """
        Enforce Nominatim policy of 1 request per second rate limit.
        """
        await asyncio.sleep(1.0)

    def _get_headers(self) -> dict[str, str]:
        """
        Construct headers ensuring User-Agent is present

        Parameters: None
        Returns:
          Dictionary of HTTP headers.
        """
        return {"User-Agent": self._settings.user_agent}

    async def search(
        self,
        query: str,
        limit: int = 5,
        countryCodes: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Search Nominatim for a text query.

        Parameters:
          query - Search string to look up.
          limit - Max number of results to return.
          countryCodes - Optional list of country codes for filtering.
        Returns: List of OSM feature dictionaries.
        """
        await self._enforce_rate_limit()

        reqParams: dict[str, Any] = {
            "q": query, 
            "format": "json",
            "addressdetails": 1,
            "limit": limit, 
        }

        # Append optional country codes if provided
        if countryCodes:
            reqParams["countrycodes"] = ",".join(countryCodes).lower()

        reqHeaders = self._get_headers() # User agent header
        reqUrl = f"{self._settings.nominatim_url}/search" # Search API format
        timeoutSeconds = self._settings.request_timeout_seconds

        try:
            # GET
            apiResponse = await self._http.get(
                reqUrl,
                params=reqParams,
                headers=reqHeaders,
                timeout=timeoutSeconds, 
            )

            if apiResponse.status_code >= 400:
                raise Exception(f"HTTP {apiResponse.status_code}")

            return apiResponse.json()

        except (httpx.TimeoutException, httpx.RequestError) as e:
            raise Exception(f"Network failure: {e}") from e

    async def reverse_geocode(self, lat: float, lon: float, zoom: int = 18) -> dict[str, Any]:
        """
        Generates an address from a coordinate given as latitude and longitude.

        Parameters:
          lat - Latitude coordinate.
          lon - Longitude coordinate.
          zoom - Level of detail for the address (0-18).
        Returns: Single OSM feature dictionary.
        """
        await self._enforce_rate_limit()

        reqParams: dict[str, Any] = {
            "lat": lat,
            "lon": lon,
            "format": "json",
            "zoom": zoom, 
        }

        reqHeaders = self._get_headers()
        reqUrl = f"{self._settings.nominatim_url}/reverse"
        timeoutSeconds = self._settings.request_timeout_seconds

        try:
            # GET
            apiResponse = await self._http.get(
                reqUrl,
                params=reqParams,
                headers=reqHeaders,
                timeout=timeoutSeconds, 
            )

            if apiResponse.status_code >= 400:
                raise Exception(f"HTTP {apiResponse.status_code}")

            return apiResponse.json()

        except (httpx.TimeoutException, httpx.RequestError) as e:
            raise Exception(f"Network failure: {e}") from e
