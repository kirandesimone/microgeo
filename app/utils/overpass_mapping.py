"""
Map overpass elements to our own models
"""

from typing import Any

from app.models.schema import OSMFeature


def map_element(element: dict[str, Any]) -> OSMFeature:
    """Convert a single Overpass element to an OSMFeature model."""

    element_type = element.get("type", "unknown")
    return OSMFeature(
        # OSM ids are unique only within type, so we need to namespace them.
        id=f"{element_type}/{element.get('id')}",
        type=element_type,
        geometry=_geometry_for(element),
        properties=element.get("tags", {}) or {},
    )


def map_elements(elements: list[dict[str, Any]]) -> list[OSMFeature]:
    """Map a list of Overpass elements, skipping any that fail validation."""

    return [map_element(element) for element in elements]


# Internal helpers

def _geometry_for(element: dict[str, Any]) -> dict[str, Any] | None:
    element_type = element.get("type")
    if element_type == "node":
        return _node_geometry(element)
    if element_type == "way":
        return _node_geometry(element)
    if element_type == "relation":
        return _relation_geometry(element)
    return None


def _node_geometry(element: dict[str, Any]) -> dict[str, Any] | None:
    lat = element.get("lat")
    lon = element.get("lon")
    if lat is None or lon is None:
        return None

    # NOTE: GeoJSON uses [lon, lat] order
    return {"type": "Point", "coordinates": [lon, lat]}


def _way_geometry(element: dict[str, Any]) -> dict[str, Any] | None:
    pass


def _relation_geometry(element: dict[str, Any]) -> dict[str, Any] | None:
    pass


def _is_closed_way(coords: list[list[float]], tags: dict[str, str]) -> bool:
    pass
