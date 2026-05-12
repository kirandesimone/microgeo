"""Tests for OverpassClient"""
import json
from pathlib import Path

import httpx
import pytest

from app.core.config import Settings
from app.services.overpass_client import OverpassClient

FIXTURES = Path(__file__).parent / "fixtures"


def _settings() -> Settings:
    return Settings()


def _client_with_handler(handler) -> tuple[OverpassClient, httpx.AsyncClient]:
    """Build an OverpassClient backed by a mocked transport.

    Returns the http client too so the test can close it.
    """
    transport = httpx.MockTransport(handler)
    http = httpx.AsyncClient(transport=transport)

    return OverpassClient(_settings(), http), http


@pytest.mark.asyncio
async def test_bbox_returns_features_from_fixture() -> None:
    fixture = json.loads((FIXTURES / "overpass_bbox_cafes.json").read_text())

    captured: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        # capture the QL body the client posted so we can start on it
        captured["body"] = request.content.decode()
        return httpx.Response(200, json=fixture)

    client, http = _client_with_handler(handler)
    try:
        features = await client.query_bbox(
            min_lat=34.0,
            min_lon=-117.2,
            max_lat=34.1,
            max_lon=-117.1,
            filters={"amenity": "cafe"},
        )
    finally:
        await http.aclose()

    assert len(features) == 3
    assert features[0]["type"] == "node"
    assert features[2]["type"] == "way"

    assert "data=" in captured["body"]
    assert "amenity" in captured["body"]
    assert "cafe" in captured["body"]


@pytest.mark.asyncio
async def test_around_returns_features() -> None:
    fixture = json.loads((FIXTURES / "overpass_bbox_cafes.json").read_text())

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=fixture)

    client, http = _client_with_handler(handler)
    try:
        features = await client.query_around_point(
            lat=34.0556,
            lon=-117.1825,
            radius_m=100.0
        )
    finally:
        await http.aclose()

    assert len(features) == 3


@pytest.mark.asyncio
async def test_empty_features_returns_empty_list() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"version": 0.6, "elements": []})

    client, http = _client_with_handler(handler)
    try:
        features = await client.query_bbox(0, 0, 1, 1)
    finally:
        await http.aclose()

    assert features == []
