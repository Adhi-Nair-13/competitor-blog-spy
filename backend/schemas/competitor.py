from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
from datetime import datetime

class CompetitorBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Name of the competitor")
    website_url: str = Field(..., description="Root website URL")
    blog_url: Optional[str] = Field(None, description="Direct blog/news page URL if known")
    rss_url: Optional[str] = Field(None, description="Direct RSS feed URL if known")
    sitemap_url: Optional[str] = Field(None, description="Direct XML sitemap URL if known")
    monitoring_enabled: bool = True

class CompetitorCreate(CompetitorBase):
    pass

class CompetitorUpdate(BaseModel):
    name: Optional[str] = None
    website_url: Optional[str] = None
    blog_url: Optional[str] = None
    rss_url: Optional[str] = None
    sitemap_url: Optional[str] = None
    monitoring_enabled: Optional[bool] = None
    selected_strategy: Optional[str] = None
    monitoring_status: Optional[str] = None

class CompetitorResponse(CompetitorBase):
    id: int
    monitoring_status: str
    selected_strategy: str
    last_checked_at: Optional[datetime] = None
    last_successful_detection_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    articles_count: Optional[int] = 0

    class Config:
        from_attributes = True

class CompetitorDetailResponse(CompetitorResponse):
    pass
