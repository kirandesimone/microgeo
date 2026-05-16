"""
Thin async client for the Overpass API.
"""

import logging
from typing import Any

import httpx

from app.core.config import Settings
from app.utils.overpass_query_builder import (
    build_around_point_query,
    build_bbox_query,
)


class OverpassClient:
    """Async wrapper around the Overpass QL endpoint.

    The OverpassClient owns query construction and execution.

    :param settings: resolves to application settings
    :param http_client: httpx.AsyncClient instance
    """

    def __init__(self, settings: Settings, http_client: httpx.AsyncClient):
        self._settings = settings
        self._http = http_client

    async def query_bbox(
        self,
        min_lat: float,
        min_lon: float,
        max_lat: float,
        max_lon: float,
        filters: dict[str, str] | None = None,
    ) -> list[dict[str, Any]]:
        """Return OSM features inside a bounding box that match `filters`.

        :param min_lat, min_lon, max_lat, max_lon: extent of query in lat/lon as 4 floats
        :param filters: dict of tag filters, e.g. {"amenity": "cafe"}
        :returns: list of OSM features, empty list if no features found"""

        query = build_bbox_query(
            min_lat=min_lat,
            min_lon=min_lon,
            max_lat=max_lat,
            max_lon=max_lon,
            filters=filters,
            timeout_seconds=self._settings.area_query_budget_seconds,
        )

        return await self._execute(query)

    async def query_around_point(
        self,
        lat: float,
        lon: float,
        radius_m: float,
        filters: dict[str, str] | None = None,
    ) -> list[dict[str, Any]]:
        """Return OSM features withing `radius_m` of point matching `filters`

        :param lat, lon: center of query in lat/lon as floats
        :param radius_m: radius of query in meters
        :param filters: dict of tag filters, e.g. {"amenity": "cafe"}
        :returns: list of OSM features, empty list if no features found"""

        query = build_around_point_query(
            lat=lat,
            lon=lon,
            radius_m=radius_m,
            filters=filters,
            timeout_seconds=self._settings.area_query_budget_seconds,
        )

        return await self._execute(query)

    async def _execute(self, query: str) -> list[dict[str, Any]]:
        """Post a QL query and return the features array"""

        try:
            response = await self._http.post(
                self._settings.overpass_url,
                data={"data": query},
                headers={
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "Accept": "application/json",
                }
            )
        except httpx.TimeoutException as e:
            raise Exception(f"Overpass timeout: {e}") from e
        except httpx.RequestError as e:
            raise Exception(f"Overpass request error: {e}") from e

        return self._parse_response(response)

    def _parse_response(self, response: httpx.Response) -> list[dict[str, Any]]:
        """Validate the HTTP response and pull out the features array.

        HTTP error codes 429 and 504 mean rate-limit and gateway timeout respectively.
        Overpass reports runtime errors via `remark` field but still returns 200."""

        if response.status_code == 400:
            raise Exception(
                "Overpass returned a 400 Bad Request: Query syntax error."
            )
        if response.status_code == 429:
            raise Exception(
                "Overpass returned a 429 Too Many Requests: Rate limit exceeded."
            )
        if response.status_code == 504:
            raise Exception("Overpass returned a 504 Gateway Timeout")
        if response.status_code >= 500:
            raise Exception(
                f"Overpass returned HTTP {response.status_code} Server Error."
            )

        # anything non-2xx at this point is an Overpass error
        if not response.is_success:
            raise Exception(f"Overpass returned an error: {response.text}")

        try:
            payload = response.json()
        except ValueError as e:
            raise Exception(f"Overpass returned invalid JSON: {e}")

        features = payload.get("elements")
        if features is None:
            # this shouldn't happen, but just in case
            return []
        if not isinstance(features, list):
            raise Exception("Overpass returned invalid JSON: no elements array")

        return features
