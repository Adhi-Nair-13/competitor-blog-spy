from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MonitoringCheckResponse(BaseModel):
    id: int
    competitor_id: int
    competitor_name: Optional[str] = None
    started_at: datetime
    completed_at: datetime
    status: str
    detection_method: str
    articles_found: int
    new_articles_found: int
    response_time_ms: float
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

class MonitoringConfigResponse(BaseModel):
    competitor_id: int
    rss_available: bool
    rss_url: Optional[str] = None
    atom_available: bool
    sitemap_available: bool
    sitemap_url: Optional[str] = None
    sitemap_index: bool
    blog_url: Optional[str] = None
    article_pattern: Optional[str] = None
    publication_date_available: bool
    structured_metadata_available: bool
    canonical_url_available: bool
    selected_strategy: str
    analysis_timestamp: datetime

    class Config:
        from_attributes = True

class NotificationResponse(BaseModel):
    id: int
    competitor_id: int
    competitor_name: Optional[str] = None
    article_id: Optional[int] = None
    title: str
    message: str
    detection_method: str
    detection_delay_seconds: Optional[float] = None
    detection_delay_formatted: Optional[str] = None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
