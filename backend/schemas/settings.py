from pydantic import BaseModel
from typing import Optional

class SettingsResponse(BaseModel):
    monitoring_interval_minutes: int
    request_timeout_seconds: int
    max_retries: int
    concurrent_workers: int
    user_agent: str
    email_notifications_enabled: bool
    smtp_host: Optional[str] = None
    smtp_port: int
    smtp_user: Optional[str] = None
    alert_email_recipient: Optional[str] = None
    demo_mode: bool
    demo_site_url: str

class SettingsUpdate(BaseModel):
    monitoring_interval_minutes: Optional[int] = None
    request_timeout_seconds: Optional[int] = None
    max_retries: Optional[int] = None
    concurrent_workers: Optional[int] = None
    user_agent: Optional[str] = None
    email_notifications_enabled: Optional[bool] = None
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    alert_email_recipient: Optional[str] = None
    demo_mode: Optional[bool] = None
