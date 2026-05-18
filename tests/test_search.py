"""
Tests for the search endpoint
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient
from app.main import app


@pytest_asyncio.fixture
async def async_client():
    """
    Fixture to provide an AsyncClient and force app lifespan execution.
    """
    # 1. The synchronous TestClient context manager forces the FastAPI app
    # to execute its lifespan (startup) events, setting up app.state.http_client.
    with TestClient(app):
        # 2. Yield the AsyncClient for the actual test HTTP requests.
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            yield client


@pytest.mark.asyncio
async def test_search_endpoint_success(async_client: AsyncClient) -> None:
    """
    Verify that the search endpoint returns a 200 and a FeatureCollection.
    """
    queryParams = {"q": "Corvallis, Oregon", "limit": 1}
    apiResponse = await async_client.get("/v1/search", params=queryParams)

    assert apiResponse.status_code == 200

    responseData = apiResponse.json()
    assert responseData["type"] == "FeatureCollection"
    assert "features" in responseData

    metaData = responseData.get("metadata", {})
    assert metaData.get("query") == "Corvallis, Oregon"


@pytest.mark.asyncio
async def test_search_with_country_filter(async_client: AsyncClient) -> None:
    """
    Verify search with country filtering params.
    """
    queryParams = {"q": "Paris", "country": ["US"]}
    apiResponse = await async_client.get("/v1/search", params=queryParams)

    assert apiResponse.status_code == 200

    responseData = apiResponse.json()
    # Check that results are in the US
    for feature in responseData.get("features", []):
        props = feature.get("properties", {})
        addressData = props.get("address", {})
        countryCode = addressData.get("country_code")
        if countryCode:
            assert countryCode == "us"
