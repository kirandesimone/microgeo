"""
High-level service layer for geocoding.
"""
from app.models.schema import BoundingBox, FeatureCollection


class GeocodeService:
    def __init__(self):
        pass

    async def features_in_area(
            self,
            bbox: BoundingBox,
            filters: dict[str, str],
    ) -> FeatureCollection:
        """Return OSM features matching `filters` inside `bbox`"""
        pass