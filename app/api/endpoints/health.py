import asyncio

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text as sql_text

from app.database.database import async_session_factory

from .schemes.health import HealthResponce

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(path="/", response_model=HealthResponce, status_code=status.HTTP_200_OK)
async def check_health() -> HealthResponce:
    """
    Perform a health check on the application.
    This endpoint checks the health status of the application by executing a database query.
    If the database is responsive within the timeout limit, the service is considered healthy.

    Raises:
        HTTPException: If the database does not respond within the specified timeout.

    Returns:
        HealthResponce: A response object indicating the health status of the application.
    """

    try:
        session = async_session_factory()
        await asyncio.wait_for(session.execute(sql_text("SELECT 1")), timeout=1)
    except asyncio.TimeoutError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE) from exc

    return HealthResponce(status="ok")
