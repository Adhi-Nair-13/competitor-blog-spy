import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Competitor Blog Spy & Real-Time Content Monitoring System"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api"
    
    # Database
    DATABASE_URL: str = "sqlite:///./blog_spy.db"
    
    # Monitoring Configuration Defaults
    DEFAULT_MONITORING_INTERVAL_MINUTES: int = 5
    REQUEST_TIMEOUT_SECONDS: int = 15
    MAX_RETRIES: int = 3
    CONCURRENT_WORKERS: int = 10
    USER_AGENT: str = "CompetitorBlogSpyBot/1.0 (+https://competitorblogspy.internal/bot; research@example.com)"
    
    # Notification & SMTP
    EMAIL_NOTIFICATIONS_ENABLED: bool = False
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    ALERT_EMAIL_RECIPIENT: Optional[str] = None
    
    # Demo & Scalability
    DEMO_MODE: bool = True
    DEMO_SITE_URL: str = "http://127.0.0.1:8001"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
