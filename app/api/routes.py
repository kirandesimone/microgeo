"""Public REST endpoints for the Geocode Location Service

Routes
------
GET /v1/features/area - features inside a bounding box

https://fastapi.tiangolo.com/reference/apirouter/
"""

from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.dependencies import GeocodeServiceDep
from app.models.schema import BoundingBox, FeatureCollection, Point

router = APIRouter(prefix="/v1", tags=["geocode"])


def _parse_filters(raw: list[str] | None) -> dict[str, str]:
    """Parse filter=key=value repeated query params into a dict

    Example: <...>?filter=amenity=cafe&filter=cuisine=italian -> {"amenity": "cafe", "cuisine": "italian"}
    """
    parsed: dict[str, str] = {}
    if not raw:
        return parsed

    for item in raw:
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        if key and value:
            parsed[key.strip()] = value.strip()

    return parsed


@router.get(
    "/features/area",
    response_model=FeatureCollection,
    status_code=status.HTTP_200_OK,
    summary="Get OSM features inside a bounding box",
)
async def get_features_in_area(
    service: GeocodeServiceDep,
    min_lat: Annotated[float, Query(ge=-90, le=90, description="Southern edge")],
    min_lon: Annotated[float, Query(ge=-180, le=180, description="Western edge")],
    max_lat: Annotated[float, Query(ge=-90, le=90, description="Northern edge")],
    max_lon: Annotated[float, Query(ge=-180, le=180, description="Eastern edge")],
    filter: Annotated[
        list[str] | None,
        Query(description="OSM tag filter, repeatable. Format: key=value"),
    ] = None,
) -> FeatureCollection:
    """Return OSM features inside a bounding box that match filter."""
    bbox = BoundingBox(
        min_lat=min_lat, min_lon=min_lon, max_lat=max_lat, max_lon=max_lon
    )

    return await service.features_in_area(bbox, _parse_filters(filter))

@router.get(
    "/features/point",
    response_model=FeatureCollection,
    status_code=status.HTTP_200_OK,
    summary="Get OSM features near a lat/lon point",
)
async def get_features_at_point(
    service: GeocodeServiceDep,
    lat: Annotated[float, Query(ge=-90, le=90, description="Latitude of the point")],
    lon: Annotated[float, Query(ge=-180, le=180, description="Longitude of the point")],
    radius: Annotated[float, Query(gt=0, description="Search radius in meters")] = 100.0,
    filter: Annotated[
        list[str] | None,
        Query(description="OSM tag filter, repeatable. Format: key=value"),
    ] = None,
) -> FeatureCollection:
    """Return OSM features within radius meters of a point matching filters."""
    point = Point(lat=lat, lon=lon)
    return await service.features_at_point(point, radius, _parse_filters(filter))


@router.get(
    "/search",
    response_model=FeatureCollection,
    status_code=status.HTTP_200_OK,
    summary="Search for a location by name or address",
)
async def search_location(
    service: GeocodeServiceDep,
    q: Annotated[str, Query(description="Search string")],
    limit: Annotated[int, Query(ge=1, le=50)] = 5,
    country: Annotated[
        list[str] | None,
        Query(description="ISO 3166-1 alpha-2 country code filter"),
    ] = None,
) -> FeatureCollection:
    """
    Search for a location by name, category, or address.

    Parameters:
      service - The geocode service dependency.
      q - The search query string.
      limit - Maximum number of results.
      country - List of country codes to filter by.
    Returns:
      A FeatureCollection of matching locations.
    """
    return await service.search(q, limit, country)
