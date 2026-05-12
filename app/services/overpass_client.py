"""
Thin async client for the Overpass API.
"""

from app.core.config import Settings

class OverpassClient:
    """Async wrapper around the Overpass QL endpoint

    """

    def __init__(self, settings: Settings):
        pass

    async def query_bbox(self, query):
        pass

    async def query_around_point(self, query):
        pass
