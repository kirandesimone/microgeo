"""
High-level service layer for geocoding.

The router layer in app.api calls into GeocodeService instead of the clients directly.
"""

import time

from app.models.schema import BoundingBox, FeatureCollection
from app.services.nominatim_client import NominatimClient
from app.services.overpass_client import OverpassClient
from app.utils.overpass_mapping import map_elements
from app.utils.nominatim_mapping import map_nominatim_results


class GeocodeService:
    def __init__(
        self, overpass: OverpassClient, nominatim: NominatimClient
    ) -> None:
        self._overpass = overpass
        self._nominatim = nominatim

    async def features_in_area(
        self,
        bbox: BoundingBox,
        filters: dict[str, str],
    ) -> FeatureCollection:
        """Return OSM features matching filters inside a BoundingBox.

        :param bbox: BoundingBox
        :param filters: dict of tag filters, e.g. {"amenity": "cafe"}
        :returns: FeatureCollection
        """

        self._validate_bbox(bbox)

        started = time.monotonic()
        elements = await self._overpass.query_bbox(
            min_lat=bbox.min_lat,
            min_lon=bbox.min_lon,
            max_lat=bbox.max_lat,
            max_lon=bbox.max_lon,
            filters=filters or None,
        )
        features = map_elements(elements)
        elapsed_ms = int((time.monotonic() - started) * 1000)

        return FeatureCollection(
            features=features,
            metadata={
                "bbox": [bbox.min_lat, bbox.min_lon, bbox.max_lat, bbox.max_lon],
                "filters": filters,
                "count": len(features),
                "elapsed_ms": elapsed_ms,
            },
        )

    @staticmethod
    def _validate_bbox(bbox: BoundingBox):
        """Helper to validate a bounding box, rejecting malformed or inverted bboxes"""

        if bbox.min_lat >= bbox.max_lat:
            raise ValueError(
                f"min_lat ({bbox.min_lat}) must be less than max_lat ({bbox.max_lat}):"
            )
        if bbox.min_lon >= bbox.max_lon:
            raise ValueError(
                f"min_lon ({bbox.min_lon}) must be less than max_lon ({bbox.max_lon}):"
            )

    async def search(
        self,
        query: str,
        limit: int = 5,
        countryCodes: list[str] | None = None,
    ) -> FeatureCollection:
        """
        Search for a location by name or address.

        Parameters:
          query - Search string to look up.
          limit - Max number of results to return.
          countryCodes - Optional list of country codes for filtering.
        Returns: List of OSM feature dictionaries.
        """
        started = time.monotonic()
        results = await self._nominatim.search(query, limit, countryCodes)
        features = map_nominatim_results(results)
        elapsedMs = int((time.monotonic() - started) * 1000)

        return FeatureCollection(
            features=features,
            metadata={
                "query": query,
                "count": len(features),
                "elapsed_ms": elapsedMs,
            },
        )
