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
                "tags": {"amenity": "cafe", "name": "Stell"},
            }
        )
        assert feature.properties == {"amenity": "cafe", "name": "Stell"}


class TestWayMapping:
    pass


class TestRelationMapping:
    pass


class TestMapElements:
    pass
