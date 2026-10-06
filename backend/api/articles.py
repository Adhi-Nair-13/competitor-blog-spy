from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc

from backend.database import get_db
from backend.models.article import Article
from backend.models.competitor import Competitor
from backend.schemas.article import ArticleResponse, ArticleDetailResponse
from backend.utils.date_helpers import format_detection_delay, get_delay_status

router = APIRouter(prefix="/articles", tags=["Articles"])

def _enrich_article(art: Article, comp_name: Optional[str] = None) -> ArticleResponse:
    delay_fmt = format_detection_delay(art.detection_delay_seconds)
    delay_lbl, _ = get_delay_status(art.detection_delay_seconds)
    
    resp = ArticleResponse(
        id=art.id,
        competitor_id=art.competitor_id,
        competitor_name=comp_name or (art.competitor.name if art.competitor else None),
        title=art.title,
        author=art.author,
        published_at=art.published_at,
        detected_at=art.detected_at,
        detection_delay_seconds=art.detection_delay_seconds,
        detection_delay_formatted=delay_fmt,
        delay_status=delay_lbl,
        detection_method=art.detection_method,
        canonical_url=art.canonical_url,
        source_url=art.source_url,
        meta_description=art.meta_description,
        featured_image=art.featured_image,
        categories=art.categories,
        tags=art.tags,
        created_at=art.created_at,
    )
    return resp

@router.get("", response_model=List[ArticleResponse])
def get_articles(
    competitor_id: Optional[int] = None,
    detection_method: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Article, Competitor.name).join(Competitor, Article.competitor_id == Competitor.id)

    if competitor_id:
        query = query.filter(Article.competitor_id == competitor_id)
    if detection_method:
        query = query.filter(Article.detection_method == detection_method)
    if search:
        s = f"%{search.strip()}%"
        query = query.filter(or_(Article.title.ilike(s), Article.content.ilike(s), Article.author.ilike(s)))

    records = query.order_by(desc(Article.detected_at)).offset(offset).limit(limit).all()
    return [_enrich_article(art, comp_name) for art, comp_name in records]

@router.get("/{id}", response_model=ArticleDetailResponse)
def get_article(id: int, db: Session = Depends(get_db)):
    art = db.query(Article).filter(Article.id == id).first()
    if not art:
        raise HTTPException(status_code=404, detail="Article not found")

    base = _enrich_article(art)
    return ArticleDetailResponse(
        **base.model_dump(),
        content=art.content,
        relevant_links=art.relevant_links,
    )
