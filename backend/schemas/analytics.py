from pydantic import BaseModel
from typing import Optional, List, Dict

class DashboardStatsResponse(BaseModel):
    total_competitors: int
    active_competitors: int
    articles_detected: int
    average_detection_time: Optional[str] = None
    average_detection_seconds: Optional[float] = None
    fastest_detection: Optional[str] = None
    fastest_detection_seconds: Optional[float] = None
    slowest_detection: Optional[str] = None
    slowest_detection_seconds: Optional[float] = None
    failed_checks: int
    total_checks: int
    success_rate_percent: float

class MethodDistribution(BaseModel):
    method: str
    count: int
    percentage: float

class CompetitorAvgDelay(BaseModel):
    competitor_id: int
    competitor_name: str
    avg_delay_seconds: float
    avg_delay_formatted: str
    articles_count: int

class TrendDataPoint(BaseModel):
    date: str
    articles_detected: int
    avg_delay_seconds: Optional[float] = None

class CheckStatusStats(BaseModel):
    status: str
    count: int

class AnalyticsResponse(BaseModel):
    method_distribution: List[MethodDistribution]
    avg_delay_by_competitor: List[CompetitorAvgDelay]
    detection_trend: List[TrendDataPoint]
    checks_distribution: List[CheckStatusStats]
