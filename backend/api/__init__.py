from fastapi import APIRouter
from backend.api.competitors import router as competitors_router
from backend.api.articles import router as articles_router
from backend.api.monitoring import router as monitoring_router
from backend.api.analytics import router as analytics_router
from backend.api.notifications import router as notifications_router
from backend.api.settings import router as settings_router
from backend.api.scale_test import router as scale_test_router
from backend.api.demo import router as demo_router

api_router = APIRouter()

api_router.include_router(competitors_router)
api_router.include_router(articles_router)
api_router.include_router(monitoring_router)
api_router.include_router(analytics_router)
api_router.include_router(notifications_router)
api_router.include_router(settings_router)
api_router.include_router(scale_test_router)
api_router.include_router(demo_router)
