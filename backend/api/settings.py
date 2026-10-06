from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.config import settings
from backend.database import get_db
from backend.models.competitor import Competitor
from backend.models.article import Article
from backend.schemas.settings import SettingsResponse, SettingsUpdate
from backend.services.monitoring_scheduler import monitoring_scheduler

router = APIRouter(prefix="", tags=["Settings & System"])

@router.get("/settings", response_model=SettingsResponse)
def get_settings():
    return SettingsResponse(
        monitoring_interval_minutes=monitoring_scheduler.interval_minutes,
        request_timeout_seconds=settings.REQUEST_TIMEOUT_SECONDS,
        max_retries=settings.MAX_RETRIES,
        concurrent_workers=settings.CONCURRENT_WORKERS,
        user_agent=settings.USER_AGENT,
        email_notifications_enabled=settings.EMAIL_NOTIFICATIONS_ENABLED,
        smtp_host=settings.SMTP_HOST,
        smtp_port=settings.SMTP_PORT,
        smtp_user=settings.SMTP_USER,
        alert_email_recipient=settings.ALERT_EMAIL_RECIPIENT,
        demo_mode=settings.DEMO_MODE,
        demo_site_url=settings.DEMO_SITE_URL,
    )

@router.post("/settings", response_model=SettingsResponse)
def update_settings(payload: SettingsUpdate):
    if payload.monitoring_interval_minutes is not None:
        settings.DEFAULT_MONITORING_INTERVAL_MINUTES = payload.monitoring_interval_minutes
        monitoring_scheduler.update_interval(payload.monitoring_interval_minutes)

    if payload.request_timeout_seconds is not None:
        settings.REQUEST_TIMEOUT_SECONDS = payload.request_timeout_seconds

    if payload.max_retries is not None:
        settings.MAX_RETRIES = payload.max_retries

    if payload.concurrent_workers is not None:
        settings.CONCURRENT_WORKERS = payload.concurrent_workers
        import asyncio
        monitoring_scheduler.concurrency_limit = payload.concurrent_workers
        monitoring_scheduler.semaphore = asyncio.Semaphore(payload.concurrent_workers)

    if payload.user_agent is not None:
        settings.USER_AGENT = payload.user_agent

    if payload.email_notifications_enabled is not None:
        settings.EMAIL_NOTIFICATIONS_ENABLED = payload.email_notifications_enabled

    if payload.smtp_host is not None:
        settings.SMTP_HOST = payload.smtp_host

    if payload.smtp_port is not None:
        settings.SMTP_PORT = payload.smtp_port

    if payload.smtp_user is not None:
        settings.SMTP_USER = payload.smtp_user

    if payload.smtp_password is not None:
        settings.SMTP_PASSWORD = payload.smtp_password

    if payload.alert_email_recipient is not None:
        settings.ALERT_EMAIL_RECIPIENT = payload.alert_email_recipient

    if payload.demo_mode is not None:
        settings.DEMO_MODE = payload.demo_mode

    return get_settings()

@router.get("/system/status")
def get_system_status(db: Session = Depends(get_db)):
    comp_count = db.query(func.count(Competitor.id)).scalar() or 0
    art_count = db.query(func.count(Article.id)).scalar() or 0
    
    return {
        "status": "HEALTHY",
        "scheduler_running": monitoring_scheduler.is_running,
        "scheduler_interval_minutes": monitoring_scheduler.interval_minutes,
        "active_concurrent_workers": monitoring_scheduler.current_running_checks,
        "configured_concurrency_limit": monitoring_scheduler.concurrency_limit,
        "total_monitored_competitors": comp_count,
        "total_stored_articles": art_count,
        "database": "CONNECTED",
        "demo_mode": settings.DEMO_MODE,
    }
