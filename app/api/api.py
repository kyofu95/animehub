from fastapi import APIRouter

from .endpoints.anime import router as anime_router
from .endpoints.auth import router as auth_router
from .endpoints.health import router as health_router
from .endpoints.user import router as user_router
from .endpoints.watchlist import router as watchentry_router

api_router = APIRouter(prefix="/api")

api_router.include_router(user_router)
api_router.include_router(auth_router)
api_router.include_router(anime_router)
api_router.include_router(watchentry_router)
api_router.include_router(health_router)
