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
        return _way_geometry(element)
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
    geom = element.get("geometry")
    if not geom:
        return None

    coords = [[pt["lon"], pt["lat"]] for pt in geom if "lat" in pt and "lon" in pt]
    if len(coords) < 2:
        # a way with one point is degenerate, treat as no geometry
        return None

    if _is_closed_way(coords, element.get("tags", {})):
        # GeoJSON polygon coordinates are a list of linear rings
        # the outer ring is the first element in the list. Currently not rebuilding inner rings.
        return {"type": "Polygon", "coordinates": [coords]}

    return {"type": "LineString", "coordinates": coords}


def _relation_geometry(element: dict[str, Any]) -> dict[str, Any] | None:
    pass


def _is_closed_way(coords: list[list[float]], tags: dict[str, str]) -> bool:
    """A way is a polygon if its endpoints meet and it's not explicitly linear.

    OSM treats a closed way is a polygon when it represents an area
        (area=yes, or has a polygon-implying tag like building, landuse, leisure)
    It's a closed line (not a polygon) when it's something like a closed road
        (highway=* on a roundabout)
    """

    if coords[0] != coords[-1]:
        return False
    if tags.get("area") == "yes":
        return True

    # These are most common keys, not complete. Full list is in the OSM wiki
    area_keys = {
        "building",
        "landuse",
        "leisure",
        "natural",
        "amenity",
        "shop",
        "tourism",
        "historic",
        "place",
        "boundary",
    }

    return any(key in tags for key in area_keys)