"""
FastAPI application factory and entry point.
"""
from collections.abc import AsyncIterator

import httpx
from fastapi import FastAPI

from app.core.config import get_settings
from app.api.status import router as status_router


async def lifespan(parent_app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()

    parent_app.state.http_client = httpx.AsyncClient(
        timeout=settings.request_timeout_seconds
        # TODO: include User-Agent header when Nominatim is implemented
    )
    try:
        yield
    finally:
        await parent_app.state.http_client.aclose()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Local microservice that wraps Overpass (OSM data) and Nominatim "
            "(geocoding) behind a small REST API."
        ),
        lifespan=lifespan
    )

    app.include_router(status_router)

    return app


app = create_app()