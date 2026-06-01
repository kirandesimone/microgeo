"""Overpass QL query builder.

Pure functions for building Overpass QL queries. Kept in own
module for unit-testing without spinning up an HTTP client or server.

The query shape produced here is::

    [out:json][timeout:N];
    (
      node<filter>(<spatial>);
      way<filter>(<spatial>);
      relation<filter>(<spatial>);
    );
    out geom;

where `<filter>` is the AND of every entry in the filter dict and
`<spatial>` is either a bbox or an `around` clause.
"""

from app.models.schema import BoundingBox


def build_bbox_query(
    bbox: BoundingBox,
    filters: dict[str, str] | None,
    timeout_seconds: float
) -> str:
    """Build a query string for features inside a BoundingBox.

     [out:json][timeout:N];
     <filter clauses>(bbox);
     out geom;
    """
    tags = _format_filters(filters)
    spatial = f"{bbox.min_lat},{bbox.min_lon},{bbox.max_lat},{bbox.max_lon}"
    timeout = _timeout_clause(timeout_seconds)

    return (
        f"[out:json][timeout:{timeout}];"
        f"("
        f"node{tags}({spatial});"
        f"way{tags}({spatial});"
        f"relation{tags}({spatial});"
        f");"
        "out geom;"
    )


def build_around_point_query(
    lat: float,
    lon: float,
    radius_m: float,
    filters: dict[str, str] | None,
    timeout_seconds: float,
) -> str:
    """Build an Overpass QL query for features within `radius_m` of a point."""
    tags = _format_filters(filters)
    around = f"around:{radius_m},{lat},{lon}"
    timeout = _timeout_clause(timeout_seconds)

    return (
        f"[out:json][timeout:{timeout}];"
        f"("
        f"node{tags}({around});"
        f"way{tags}({around});"
        f"relation{tags}({around});"
        f");"
        f"out geom;"
    )



def _timeout_clause(budget_seconds: float) -> int:
    """Convert the configured timeout float into the integer seconds Overpass expects."""
    return max(1, int(budget_seconds))


def _format_filters(filters: dict[str, str] | None) -> str:
    """Build the tag-filter brackets from a single element selector."""

    if not filters:
        return ""

    parts = []
    for key in sorted(filters):
        value = filters[key]
        parts.append(f'["{_escape(key)}"="{_escape(value)}"]')

    return "".join(parts)


def _escape(literal: str) -> str:
    """Escape a string for including as a double-quoted Overpass QL literal"""
    return literal.translate(str.maketrans({"\\": "\\\\", '"': '\\"'}))
