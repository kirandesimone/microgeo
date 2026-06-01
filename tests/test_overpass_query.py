
from app.models.schema import BoundingBox
from app.utils.overpass_query_builder import (
    build_bbox_query,
    build_around_point_query,
    _format_filters,
    _escape
)


class TestEscape:
    def test_no_special_chars_passes_through(self) -> None:
        assert _escape("cafe") == "cafe"

    def test_double_quote_is_escaped(self) -> None:
        assert _escape('say "hi"') == 'say \\"hi\\"'

    def test_backslash_is_escaped(self) -> None:
        assert _escape("a\\b") == "a\\\\b"

    def test_colon_is_left_alone(self) -> None:
        # Colons appear in OSM keys like 'addr:housenumber'.
        # They're safe inside Overpass QL quoted literals.
        assert _escape("addr:housenumber") == "addr:housenumber"

    def test_non_ascii_passes_through(self) -> None:
        assert _escape("Gielgenstraße") == "Gielgenstraße"


class TestFormatFilters:
    def test_none_returns_empty(self) -> None:
        assert _format_filters(None) == ""

    def test_empty_dict_returns_empty(self) -> None:
        assert _format_filters({}) == ""

    def test_single_filter(self) -> None:
        assert _format_filters({"amenity": "cafe"}) == '["amenity"="cafe"]'


class TestBuildBboxQuery:
    def test_basic_shape(self) -> None:
        test_query = build_bbox_query(
            bbox=BoundingBox(
                min_lat=34.0,
                min_lon=-117.2,
                max_lat=34.1,
                max_lon=-117.1,
            ),
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


class TestBuildAroundPointQuery:
    def test_basic_shape(self) -> None:
        query = build_around_point_query(
            lat=34.0556,
            lon=-117.1825,
            radius_m=50.0,
            filters={"amenity": "cafe"},
            timeout_seconds=3.0,
        )
        assert "around:50.0,34.0556,-117.1825" in query
        assert 'node["amenity"="cafe"]' in query
        assert 'way["amenity"="cafe"]' in query
        assert 'relation["amenity"="cafe"]' in query
