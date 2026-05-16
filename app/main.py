"""
FastAPI application factory and entry point.
"""
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

import httpx
from fastapi import FastAPI

from app.core.config import get_settings
from app.api.status import router as status_router
from app.api.routes import router as api_router


# https://docs.python.org/3/library/contextlib.html#contextlib.asynccontextmanager
@asynccontextmanager
async def lifespan(parent_app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()

    parent_app.state.http_client = httpx.AsyncClient(
        timeout=settings.request_timeout_seconds,
        headers={
            "User-Agent": f"{settings.user_agent}",
            "Accept": "application/json",
        }
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
    app.include_router(api_router)

    return app


app = create_app()