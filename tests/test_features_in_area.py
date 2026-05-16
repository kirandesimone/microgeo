"""Service-layer tests for `GeocodeServie.features_in_area`"""

from typing import Any
from unittest.mock import AsyncMock

import pytest

from app.models.schema import BoundingBox
from app.services.geocode import GeocodeService


def _make_service(elements: list[dict[str, Any]] | Exception) -> GeocodeService:
    """Create a GeocodeService whose Overpass client returns elements"""

    overpass = AsyncMock()
    if isinstance(elements, Exception):
        overpass.query_bbox.side_effect = elements
    else:
        overpass.query_bbox.return_value = elements

    nomination = AsyncMock() # not used by features_in_area

    return GeocodeService(overpass=overpass, nominatim=nomination)


@pytest.mark.asyncio
async def test_empty_result_returns_empty_collection_with_metadata() -> None:
    service = _make_service([])
    result = await service.features_in_area(
        BoundingBox(min_lat=34.0, min_lon=-117.2, max_lat=34.1, max_lon=-117.1),
        filters={"amenity": "cafe"},
    )

    assert result.type == "FeatureCollection"
    assert result.features == []
    assert result.metadata["count"] == 0
    assert result.metadata["bbox"] == [34.0, -117.2, 34.1, -117.1]
    assert result.metadata["filters"] == {"amenity": "cafe"}
    assert "elapsed_ms" in result.metadata


@pytest.mark.asyncio
async def test_single_node_result() -> None:
    service = _make_service(
        [
            {
                "type": "node",
                "id": 1,
                "lat": 34.0556,
                "lon": -117.1825,
                "tags": {"amenity": "cafe", "name": "Augie's"},
            }
        ]
    )
    result = await service.features_in_area(
        BoundingBox(min_lat=34.0, min_lon=-117.2, max_lat=34.1, max_lon=-117.1),
        filters={"amenity": "cafe"},
    )
    assert result.metadata["count"] == 1
    assert len(result.features) == 1

    feature = result.features[0]

    assert feature.id == "node/1"
    assert feature.properties["name"] == "Augie's"
