from fastapi import APIRouter
from app.api.api_v1.endpoints import translation, languages

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(translation.router, prefix="/translate", tags=["translation"])
api_router.include_router(languages.router, prefix="/languages", tags=["languages"])
