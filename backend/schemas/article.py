from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ArticleResponse(BaseModel):
    id: int
    competitor_id: int
    competitor_name: Optional[str] = None
    title: str
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    detected_at: datetime
    detection_delay_seconds: Optional[float] = None
    detection_delay_formatted: Optional[str] = None
    delay_status: Optional[str] = None
    detection_method: str
    canonical_url: str
    source_url: str
    meta_description: Optional[str] = None
    featured_image: Optional[str] = None
    categories: Optional[str] = None
    tags: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ArticleDetailResponse(ArticleResponse):
    content: Optional[str] = None
    relevant_links: Optional[str] = None
