import logging
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.models.competitor import Competitor
from backend.models.article import Article
from backend.models.monitoring_config import MonitoringConfiguration
from backend.schemas.competitor import CompetitorCreate, CompetitorUpdate, CompetitorResponse, CompetitorDetailResponse
from backend.schemas.monitoring import MonitoringConfigResponse
from backend.services.website_analyzer import WebsiteAnalyzer
from backend.services.monitoring_scheduler import monitoring_scheduler

router = APIRouter(prefix="/competitors", tags=["Competitors"])
logger = logging.getLogger(__name__)

@router.get("", response_model=List[CompetitorResponse])
def get_competitors(db: Session = Depends(get_db)):
    competitors = db.query(Competitor).order_by(Competitor.created_at.desc()).all()
    results = []
    for c in competitors:
        art_count = db.query(func.count(Article.id)).filter(Article.competitor_id == c.id).scalar() or 0
        c_dict = CompetitorResponse.model_validate(c)
        c_dict.articles_count = art_count
        results.append(c_dict)
    return results

@router.post("", response_model=CompetitorResponse)
async def create_competitor(comp_in: CompetitorCreate, db: Session = Depends(get_db)):
    # Create competitor entry
    competitor = Competitor(
        name=comp_in.name.strip(),
        website_url=comp_in.website_url.strip(),
        blog_url=comp_in.blog_url.strip() if comp_in.blog_url else None,
        rss_url=comp_in.rss_url.strip() if comp_in.rss_url else None,
        sitemap_url=comp_in.sitemap_url.strip() if comp_in.sitemap_url else None,
        monitoring_enabled=comp_in.monitoring_enabled,
        monitoring_status="CHECKING",
        selected_strategy="Analyzing...",
    )
    db.add(competitor)
    db.commit()
    db.refresh(competitor)

    # Automatically analyze the website
    analyzer = WebsiteAnalyzer()
    try:
        analysis_result = await analyzer.analyze_website(
            root_url=competitor.website_url,
            user_blog_url=competitor.blog_url,
            user_rss_url=competitor.rss_url,
            user_sitemap_url=competitor.sitemap_url,
        )

        config = MonitoringConfiguration(
            competitor_id=competitor.id,
            rss_available=analysis_result["rss_available"],
            rss_url=analysis_result["rss_url"],
            atom_available=analysis_result["atom_available"],
            sitemap_available=analysis_result["sitemap_available"],
            sitemap_url=analysis_result["sitemap_url"],
            sitemap_index=analysis_result["sitemap_index"],
            blog_url=analysis_result["blog_url"],
            article_pattern=analysis_result["article_pattern"],
            publication_date_available=analysis_result["publication_date_available"],
            structured_metadata_available=analysis_result["structured_metadata_available"],
            canonical_url_available=analysis_result["canonical_url_available"],
            selected_strategy=analysis_result["selected_strategy"],
        )
        db.add(config)

        # Update competitor fields if analyzer discovered better URLs
        if not competitor.rss_url and analysis_result["rss_url"]:
            competitor.rss_url = analysis_result["rss_url"]
        if not competitor.sitemap_url and analysis_result["sitemap_url"]:
            competitor.sitemap_url = analysis_result["sitemap_url"]
        if not competitor.blog_url and analysis_result["blog_url"]:
            competitor.blog_url = analysis_result["blog_url"]

        competitor.selected_strategy = analysis_result["selected_strategy"]
        competitor.monitoring_status = "ONLINE"
        db.commit()
        db.refresh(competitor)

        # Trigger immediate initial check in background
        if competitor.monitoring_enabled:
            import asyncio
            asyncio.create_task(monitoring_scheduler.check_single_competitor_with_worker(competitor.id))

    except Exception as e:
        logger.error(f"Website analysis error for {competitor.name}: {e}")
        competitor.monitoring_status = "ONLINE"
        competitor.selected_strategy = "Direct Page"
        db.commit()

    art_count = db.query(func.count(Article.id)).filter(Article.competitor_id == competitor.id).scalar() or 0
    resp = CompetitorResponse.model_validate(competitor)
    resp.articles_count = art_count
    return resp

@router.get("/{id}")
def get_competitor(id: int, db: Session = Depends(get_db)):
    competitor = db.query(Competitor).filter(Competitor.id == id).first()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")

    art_count = db.query(func.count(Article.id)).filter(Article.competitor_id == competitor.id).scalar() or 0
    config_dict = None
    if competitor.configuration:
        config_dict = MonitoringConfigResponse.model_validate(competitor.configuration)

    return {
        "competitor": CompetitorResponse.model_validate(competitor),
        "articles_count": art_count,
        "configuration": config_dict,
    }

@router.put("/{id}", response_model=CompetitorResponse)
def update_competitor(id: int, update_data: CompetitorUpdate, db: Session = Depends(get_db)):
    competitor = db.query(Competitor).filter(Competitor.id == id).first()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")

    data = update_data.model_dump(exclude_unset=True)
    for field, val in data.items():
        setattr(competitor, field, val)

    competitor.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(competitor)

    art_count = db.query(func.count(Article.id)).filter(Article.competitor_id == competitor.id).scalar() or 0
    resp = CompetitorResponse.model_validate(competitor)
    resp.articles_count = art_count
    return resp

@router.delete("/{id}")
def delete_competitor(id: int, db: Session = Depends(get_db)):
    competitor = db.query(Competitor).filter(Competitor.id == id).first()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")

    db.delete(competitor)
    db.commit()
    return {"message": f"Competitor '{competitor.name}' and all associated records deleted."}

@router.post("/{id}/analyze", response_model=MonitoringConfigResponse)
async def reanalyze_competitor(id: int, db: Session = Depends(get_db)):
    competitor = db.query(Competitor).filter(Competitor.id == id).first()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")

    analyzer = WebsiteAnalyzer()
    analysis_result = await analyzer.analyze_website(
        root_url=competitor.website_url,
        user_blog_url=competitor.blog_url,
        user_rss_url=competitor.rss_url,
        user_sitemap_url=competitor.sitemap_url,
    )

    config = competitor.configuration
    if not config:
        config = MonitoringConfiguration(competitor_id=competitor.id)
        db.add(config)

    config.rss_available = analysis_result["rss_available"]
    config.rss_url = analysis_result["rss_url"]
    config.atom_available = analysis_result["atom_available"]
    config.sitemap_available = analysis_result["sitemap_available"]
    config.sitemap_url = analysis_result["sitemap_url"]
    config.sitemap_index = analysis_result["sitemap_index"]
    config.blog_url = analysis_result["blog_url"]
    config.article_pattern = analysis_result["article_pattern"]
    config.publication_date_available = analysis_result["publication_date_available"]
    config.structured_metadata_available = analysis_result["structured_metadata_available"]
    config.canonical_url_available = analysis_result["canonical_url_available"]
    config.selected_strategy = analysis_result["selected_strategy"]
    config.analysis_timestamp = datetime.now(timezone.utc)

    competitor.selected_strategy = analysis_result["selected_strategy"]
    db.commit()
    db.refresh(config)
    return config

@router.post("/{id}/check")
async def trigger_check(id: int, db: Session = Depends(get_db)):
    competitor = db.query(Competitor).filter(Competitor.id == id).first()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")

    from backend.services.detection_engine import DetectionEngine
    engine = DetectionEngine(db)
    check = await engine.run_check_for_competitor(id)
    return {
        "status": check.status,
        "articles_found": check.articles_found,
        "new_articles_found": check.new_articles_found,
        "response_time_ms": check.response_time_ms,
        "error_message": check.error_message,
        "strategy": check.detection_method,
    }
