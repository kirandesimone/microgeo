"""
Thin async client for the Overpass API.
"""
from typing import Any

import httpx

from app.core.config import Settings
from app.utils.overpass_query_builder import build_around_point_query, build_bbox_query

class OverpassClient:
    """Async wrapper around the Overpass QL endpoint"""

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
        """Return OSM features inside a bounding box that match `filters`."""
        query = build_bbox_query(
            min_lat=min_lat,
            min_lon=min_lon,
            max_lat=max_lat,
            max_lon=max_lon,
            filters=filters,
            timeout_seconds=self._settings.area_query_budget_seconds
        )

        return await self._execute(query)


    async def query_around_point(
        self,
        lat: float,
        lon: float,
        radius_m: float,
        filters: dict[str, str] | None = None,
    ) -> list[dict[str, Any]]:
        """Return OSM features withing `radius_m` of point matching `filters`"""
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
            )
        except httpx.TimeoutException as e:
            print(f"overpass timeout: {e}")
        except httpx.RequestError as e:
            print(f"overpass request error: {e}")

        return self._parse_response(response)


    def _parse_response(self, response: httpx.Response) -> list[dict[str, Any]]:
        """Validate the HTTP response and pull out the features array."""
        if response.status_code == 504:
            raise Exception("Overpass returned a 504 Gateway Timeout")
        # TODO: handle other error codes

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
