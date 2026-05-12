
from app.services.overpass_client import (
    _build_bbox_query,
    _format_filters,
)


class TestFormatFilters:
    def test_none_returns_empty(self) -> None:
        assert _format_filters(None) == ""

    def test_empty_dict_returns_empty(self) -> None:
        assert _format_filters({}) == ""

    def test_single_filter(self) -> None:
        assert _format_filters({"amenity": "cafe"}) == '["amenity"="cafe"]'


class TestBuildBboxQuery:
    def test_basic_shape(self) -> None:
        test_query = _build_bbox_query(
            min_lat=34.0,
            min_lon=-117.2,
            max_lat=34.1,
            max_lon=-117.1,
            filters={"amenity": "cafe"},
            timeout_seconds=3.0,
        )
        assert test_query == (
            "[out:json][timeout:3];"
            "("
            'node["amenity"="cafe"](34.0,-117.2,34.1,-117.1);'
            'way["amenity"="cafe"](34.0,-117.2,34.1,-117.1);'
            'relation["amenity"="cafe"](34.0,-117.2,34.1,-117.1);'
            ");"
            "out geom;"
        )