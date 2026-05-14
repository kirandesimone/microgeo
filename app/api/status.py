"""Status and readiness of the service"""

from fastapi import APIRouter

from app.core.config import get_settings


router = APIRouter(tags=["status"])


@router.get("/status", summary="Get the status of the service")
async def get_status() -> dict[str, str]:
    """Returns 200 if the process is up. Does not check other apis"""

    settings = get_settings()
    return {"status": "ok", "service": settings.app_name, "version": settings.app_version}


@router.get("/ready", summary="Check if the service is ready to accept requests")
async def get_ready() -> dict[str, str]:
    """Returns 200 if the service is ready to accept requests."""

    # TODO: check Overpass and Nominatim are ready

    return {"status": "ready"}