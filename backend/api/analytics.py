from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.models.competitor import Competitor
from backend.models.article import Article
from backend.models.monitoring_check import MonitoringCheck
from backend.schemas.analytics import (
    DashboardStatsResponse, AnalyticsResponse,
    MethodDistribution, CompetitorAvgDelay, TrendDataPoint, CheckStatusStats
)
from backend.utils.date_helpers import format_detection_delay

router = APIRouter(prefix="", tags=["Analytics & Dashboard"])

@router.get("/dashboard/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_comp = db.query(func.count(Competitor.id)).scalar() or 0
    active_comp = db.query(func.count(Competitor.id)).filter(Competitor.monitoring_enabled == True).scalar() or 0
    total_articles = db.query(func.count(Article.id)).scalar() or 0

    # Delay statistics
    delays = db.query(Article.detection_delay_seconds).filter(Article.detection_delay_seconds.isnot(None)).all()
    delay_values = [d[0] for d in delays if d[0] is not None]

    avg_sec = (sum(delay_values) / len(delay_values)) if delay_values else None
    min_sec = min(delay_values) if delay_values else None
    max_sec = max(delay_values) if delay_values else None

    # Checks statistics
    total_checks = db.query(func.count(MonitoringCheck.id)).scalar() or 0
    failed_checks = db.query(func.count(MonitoringCheck.id)).filter(MonitoringCheck.status == "FAILED").scalar() or 0
    success_rate = round(((total_checks - failed_checks) / total_checks * 100), 1) if total_checks > 0 else 100.0

    return DashboardStatsResponse(
        total_competitors=total_comp,
        active_competitors=active_comp,
        articles_detected=total_articles,
        average_detection_time=format_detection_delay(avg_sec),
        average_detection_seconds=avg_sec,
        fastest_detection=format_detection_delay(min_sec),
        fastest_detection_seconds=min_sec,
        slowest_detection=format_detection_delay(max_sec),
        slowest_detection_seconds=max_sec,
        failed_checks=failed_checks,
        total_checks=total_checks,
        success_rate_percent=success_rate,
    )

@router.get("/analytics", response_model=AnalyticsResponse)
def get_analytics(db: Session = Depends(get_db)):
    # 1. Detection Method Distribution
    method_counts = db.query(Article.detection_method, func.count(Article.id)).group_by(Article.detection_method).all()
    total_articles = sum(c[1] for c in method_counts) if method_counts else 0

    methods_dist = []
    for method, count in method_counts:
        pct = round((count / total_articles * 100), 1) if total_articles > 0 else 0
        methods_dist.append(MethodDistribution(method=method or "Unknown", count=count, percentage=pct))

    # 2. Average Detection Time by Competitor
    comp_delays = (
        db.query(
            Competitor.id,
            Competitor.name,
            func.avg(Article.detection_delay_seconds),
            func.count(Article.id)
        )
        .join(Article, Competitor.id == Article.competitor_id)
        .filter(Article.detection_delay_seconds.isnot(None))
        .group_by(Competitor.id, Competitor.name)
        .all()
    )

    comp_delay_list = []
    for cid, cname, avg_d, count in comp_delays:
        comp_delay_list.append(CompetitorAvgDelay(
            competitor_id=cid,
            competitor_name=cname,
            avg_delay_seconds=round(avg_d or 0, 1),
            avg_delay_formatted=format_detection_delay(avg_d),
            articles_count=count,
        ))

    # 3. Detection Trend by Date
    trend_query = (
        db.query(
            func.strftime("%Y-%m-%d", Article.detected_at).label("day"),
            func.count(Article.id),
            func.avg(Article.detection_delay_seconds)
        )
        .group_by("day")
        .order_by("day")
        .limit(30)
        .all()
    )

    trend_list = [
        TrendDataPoint(date=day or "N/A", articles_detected=cnt, avg_delay_seconds=round(avg_d or 0, 1) if avg_d else None)
        for day, cnt, avg_d in trend_query
    ]

    # 4. Check Status Stats (SUCCESS vs FAILED)
    status_query = db.query(MonitoringCheck.status, func.count(MonitoringCheck.id)).group_by(MonitoringCheck.status).all()
    checks_dist = [CheckStatusStats(status=st, count=cnt) for st, cnt in status_query]

    return AnalyticsResponse(
        method_distribution=methods_dist,
        avg_delay_by_competitor=comp_delay_list,
        detection_trend=trend_list,
        checks_distribution=checks_dist,
    )
