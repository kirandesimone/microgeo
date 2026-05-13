"""Service-layer tests for `GeocodeServie.features_in_area`"""

from typing import Any
from unittest.mock import AsyncMock

from app.services.geocode import GeocodeService


def _make_service(elements: list[dict[str, Any]] | Exception) -> GeocodeService:
    """Build a GeocodeService whose Overpass client returns `elements`"""
    pass
