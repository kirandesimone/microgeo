"""Contract tests for the public API.

These don't call the API endpoints, but just check the framework is
wired correctly: routs mount, query validation runs, and error responses
are correct.

https://fastapi.tiangolo.com/tutorial/testing/
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    # Context manager triggers FastAPI lifespan, which
    # inits the shared httpx.AsyncClient on app.state.
    with TestClient(app) as client:
        yield client


def test_status_returns_200(client: TestClient) -> None:
    result = client.get("/status")

    assert result.status_code == 200
    assert result.json()["status"] == "ok"


def test_ready_returns_200(client: TestClient) -> None:
    result = client.get("/ready")

    assert result.status_code == 200


def test_area_endpoint_validates_bbox(client: TestClient) -> None:
    # min_lat out of range -> from query validation
    result = client.get(
        "/v1/features/area",
        params={"min_lat": -200, "min_lon": 0, "max_lat": 1, "max_lon": 1}
    )

    assert result.status_code == 422
