"""FastAPI dependency providers.

The httpx.AsyncClient is created once during the lifespan event
and stored on app.state. The providers pull from the shared
 instance, so connection pools are reused across requests.

 https://fastapi.tiangolo.com/tutorial/dependencies/
"""
from typing import Annotated

import httpx
from fastapi import Depends, Request

from app.core.config import Settings, get_settings
from app.services.geocode import GeocodeService
from app.services.nominatim_client import NominatimClient
from app.services.overpass_client import OverpassClient


# https://fastapi.tiangolo.com/tutorial/dependencies/#share-annotated-dependencies
SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_http_client(request: Request) -> httpx.AsyncClient:
    """Get the httpx.AsyncClient from the app state."""
    return request.app.state.http_client


def get_overpass_client(
    settings: SettingsDep,
    http_client: Annotated[httpx.AsyncClient, Depends(get_http_client)]
) -> OverpassClient:
    return OverpassClient(settings, http_client)


def get_nominatim_client(
    settings: SettingsDep,
    http_client: Annotated[httpx.AsyncClient, Depends(get_http_client)]
) -> NominatimClient:
    return NominatimClient(settings, http_client)


def get_geocode_service(
    overpass: Annotated[OverpassClient, Depends(get_overpass_client)],
    nominatim: Annotated[NominatimClient, Depends(get_nominatim_client)]
) -> GeocodeService:
    return GeocodeService(overpass, nominatim)


GeocodeServiceDep = Annotated[GeocodeService, Depends(get_geocode_service)]
