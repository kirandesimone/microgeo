"""
Map Nominatim search results to our own models.
"""

from typing import Any
from app.models.schema import OSMFeature


def map_nominatim_result(result: dict[str, Any]) -> OSMFeature:
    """
    Convert a single Nominatim result to an OSMFeature model.
    """
    osmType = result.get("osm_type", "unknown")
    osmId = result.get("osm_id")

    # Nominatim returns lat/lon as strings; convert to float
    try:
        lat = float(result.get("lat", 0))
        lon = float(result.get("lon", 0))
    except (ValueError, TypeError):
        lat, lon = 0.0, 0.0

    return OSMFeature(
        # Namespace the ID since OSM IDs are only unique within a type
        id=(
            f"{osmType}/{osmId}" if osmId else f"unknown/{result.get('place_id')}"
        ),
        type=osmType,
        geometry={"type": "Point", "coordinates": [lon, lat]},
        properties={
            "display_name": result.get("display_name"),
            "address": result.get("address", {}),
            "place_id": result.get("place_id"),
            "importance": result.get("importance"),
        },
    )


def map_nominatim_results(results: list[dict[str, Any]]) -> list[OSMFeature]:
    """
    Map a list of Nominatim results.
    """
    return [map_nominatim_result(result) for result in results]
