"""
Tests for Nominatim Client
"""

import httpx
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.core.config import Settings
from app.services.nominatim_client import NominatimClient

@pytest.fixture
def _test_settings() -> Settings:
    """
    Provide a Settings instance for testing.
    """
    return Settings()

@pytest.fixture
def _mock_http_client() -> AsyncMock:
    """
    Provide a mocked httpx.AsyncClient.
    """
    return AsyncMock(spec=httpx.AsyncClient)

def test_missing_user_agent() -> None:
    """
    Verify ValueError is raised when User-Agent is missing.
    """
    _bad_settings = MagicMock(spec=Settings)
    _bad_settings.user_agent = "" # Test empty user agent
    _mock_http = AsyncMock()

    with pytest.raises(ValueError, match="A valid User-Agent is required."):
        NominatimClient(_bad_settings, _mock_http)

@pytest.mark.asyncio
async def test_search_basic_query(
        _test_settings: Settings,
        _mock_http_client: AsyncMock, 
) -> None:
    """
    Verify basic search request formatting and response.    
    """
    _mock_resp = MagicMock()
    _mock_resp.status_code = 200
    _mock_resp.json.return_value = [{"place_id": 1}]
    _mock_http_client.get.return_value = _mock_resp

    _client = NominatimClient(_test_settings, _mock_http_client)
    _searchRes = await _client.search(query="Los Angeles")

    assert len(_searchRes) == 1
    _mock_http_client.get.assert_called_once()

    # Extract kwargs from mock call
    _, _callKws = _mock_http_client.get.call_args
    assert _callKws["params"]["q"] == "Los Angeles"

    _expectedUa = _test_settings.user_agent
    assert _callKws["headers"]["User-Agent"] == _expectedUa

@pytest.mark.asyncio
async def test_search_country_filter(
    _test_settings: Settings,
    _mock_http_client: AsyncMock,
) -> None:
    """
    Verify country filter parameter logic.
    """
    _mockResp = MagicMock()
    _mockResp.status_code = 200
    _mockResp.json.return_value = []
    _mock_http_client.get.return_value = _mockResp

    _client = NominatimClient(_test_settings, _mock_http_client)
    await _client.search(query="Paris", countryCodes=["FR"])

    _, _callKws = _mock_http_client.get.call_args
    assert _callKws["params"]["countrycodes"] == "fr"

@pytest.mark.asyncio
async def test_search_empty_result(
    _test_settings: Settings,
    _mock_http_client: AsyncMock,
) -> None:
    """
    Verify empty list is handled correctly.
    """
    _mockResp = MagicMock()
    _mockResp.status_code = 200
    _mockResp.json.return_value = []
    _mock_http_client.get.return_value = _mockResp

    _client = NominatimClient(_test_settings, _mock_http_client)
    _searchRes = await _client.search(query="Nowhere")

    assert _searchRes == []


@pytest.mark.asyncio
async def test_network_timeout(
    _test_settings: Settings,
    _mock_http_client: AsyncMock,
) -> None:
    """
    Verify httpx timeouts are caught and re-raised.
    """
    _mock_http_client.get.side_effect = httpx.TimeoutException("Timeout")

    _client = NominatimClient(_test_settings, _mock_http_client)

    with pytest.raises(Exception, match="Network failure"):
        await _client.search(query="TimeoutCity")

@pytest.mark.asyncio
async def test_reverse_geocode_integration(
    _test_settings: Settings,
    _mock_http_client: AsyncMock,
) -> None:
    """
    Verify reverse geocode endpoint formatting against fixture.
    """
    _mockResp = MagicMock()
    _mockResp.status_code = 200
    _mockFixture = {"place_id": 2, "name": "Fake St"}
    _mockResp.json.return_value = _mockFixture
    _mock_http_client.get.return_value = _mockResp

    _client = NominatimClient(_test_settings, _mock_http_client)
    
    # Coordinate test utilizing Los Angeles coordinates
    _geoRes = await _client.reverse_geocode(lat=34.05, lon=-118.24)

    assert _geoRes["place_id"] == 2
    _mock_http_client.get.assert_called_once()
    
    _, _callKws = _mock_http_client.get.call_args
    assert _callKws["params"]["lat"] == 34.05
    assert _callKws["params"]["lon"] == -118.24
