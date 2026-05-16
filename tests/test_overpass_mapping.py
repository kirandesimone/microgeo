"""Unit tests for the Overpass-element-to-OSMFeature mapping.

No service, no network; only shape transformations.
"""

from app.utils.overpass_mapping import map_element, map_elements


class TestNodeMapping:
    def test_node_becomes_point_with_lonlat_order(self) -> None:
        feature = map_element(
            {"type": "node", "id": 42, "lat": 34.05, "lon": -117.18, "tags": {}}
        )
        assert feature.type == "node"
        assert feature.id == "node/42"
        assert feature.geometry == {
            "type": "Point",
            "coordinates": [-117.18, 34.05]
        }

    def test_node_tags_become_properties(self) -> None:
        feature = map_element(
            {
                "type": "node",
                "id": 1,
                "lat": 0,
                "lon": 0,
                "tags": {"amenity": "cafe", "name": "Stell"}
            }
        )
        assert feature.properties == {"amenity": "cafe", "name": "Stell"}


class TestWayMapping:
    def test_open_way_becomes_linestring(self) -> None:
        element = {
            "type": "way",
            "id": 100,
            "geometry": [
                {"lat": 0.0, "lon": 0.0},
                {"lat": 1.0, "lon": 1.0},
                {"lat": 2.0, "lon": 2.0},
            ],
            "tags": {"highway": "residential"}
        }
        feature = map_element(element)

        assert feature.id == "way/100"
        assert feature.geometry == {
            "type": "LineString",
            "coordinates": [[0.0, 0.0], [1.0, 1.0], [2.0, 2.0]]
        }


    def test_closed_building_way_becomes_polygon(self) -> None:
        # first and last coordinates match AND has a polygon-implying tag
        element = {
            "type": "way",
            "id": 200,
            "geometry": [
                {"lat": 0.0, "lon": 0.0},
                {"lat": 0.0, "lon": 1.0},
                {"lat": 1.0, "lon": 1.0},
                {"lat": 1.0, "lon": 0.0},
                {"lat": 0.0, "lon": 0.0}
            ],
            "tags": {"building": "yes"}
        }
        feature = map_element(element)

        assert feature.geometry is not None
        assert feature.geometry["type"] == "Polygon"
        # GeoJSON polygon coords are wrapped in a ring list
        assert len(feature.geometry["coordinates"]) == 1
        assert len(feature.geometry["coordinates"][0]) == 5


    def test_closed_road_stays_linestring(self) -> None:
        # A roundabout is a closed way but NOT a polygon
        element = {
            "type": "way",
            "id": 300,
            "geometry": [
                {"lat": 0.0, "lon": 0.0},
                {"lat": 0.0, "lon": 1.0},
                {"lat": 1.0, "lon": 0.0},
                {"lat": 0.0, "lon": 0.0}
            ],
            "tags": {"highway": "primary", "junction": "roundabout"}
        }
        feature = map_element(element)

        assert feature.geometry is not None
        assert feature.geometry["type"] == "LineString"


class TestRelationMapping:
    def test_relation_becomes_geometry_collection(self) -> None:
        element = {
            "type": "relation",
            "id": 500,
            "members": [
                {
                    "type": "way",
                    "ref": 1,
                    "role": "outer",
                    "geometry": [
                        {"lat": 0.0, "lon": 0.0},
                        {"lat": 1.0, "lon": 1.0}
                    ]
                },
                {
                    "type": "way",
                    "ref": 2,
                    "role": "inner",
                    "geometry": [
                        {"lat": 0.2, "lon": 0.2},
                        {"lat": 0.3, "lon": 0.3}
                    ]
                }
            ],
            "tags": {"type": "multipolygon"}
        }
        feature = map_element(element)

        assert feature.id == "relation/500"
        assert feature.geometry is not None
        assert feature.geometry["type"] == "GeometryCollection"
        assert len(feature.geometry["geometries"]) == 2


    def test_relation_with_no_geometric_members_returns_none(self) -> None:
        element = {
            "type": "relation",
            "id": 600,
            "members": [
                {"type": "relation", "ref": 999,"role": "child"}
            ],
            "tags": {}
        }
        feature = map_element(element)

        assert feature.geometry is None


class TestMapElements:

    def test_empty_input_returns_empty_list(self) -> None:
        assert map_elements([]) == []


    def test_mixed_types_all_pass_through(self) -> None:
        elements = [
            {"type": "node", "id": 1, "lat": 0, "lon": 0, "tags": {}},
            {
                "type": "way",
                "id": 2,
                "geometry": [
                    {"lat": 0.0, "lon": 0.0},
                    {"lat": 1.0, "lon": 1.0}
                ],
                "tags": {}
            },
            {"type": "relation", "id": 3, "members": [], "tags": {}}
        ]
        features = map_elements(elements)

        assert [feature.type for feature in features] == ["node", "way", "relation"]
        assert [feature.id for feature in features] == ["node/1", "way/2", "relation/3"]
