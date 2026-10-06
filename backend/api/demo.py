import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import httpx

from backend.config import settings
from backend.database import get_db
from backend.models.competitor import Competitor
from backend.schemas.competitor import CompetitorCreate
from backend.api.competitors import create_competitor

router = APIRouter(prefix="/demo", tags=["Demo Site Helper"])
logger = logging.getLogger(__name__)

@router.post("/seed")
async def seed_demo_competitor(db: Session = Depends(get_db)):
    """
    Convenient 1-click helper: Registers the controlled demo website
    as a competitor in the database and triggers automatic investigation.
    """
    demo_url = settings.DEMO_SITE_URL
    existing = db.query(Competitor).filter(Competitor.website_url == demo_url).first()
    if existing:
        return {"status": "exists", "competitor_id": existing.id, "message": "Demo competitor is already registered."}

    comp_payload = CompetitorCreate(
        name="Acme Tech Blog (Demo Site)",
        website_url=demo_url,
        blog_url=f"{demo_url}/blog",
        rss_url=f"{demo_url}/rss.xml",
        sitemap_url=f"{demo_url}/sitemap.xml",
        monitoring_enabled=True,
    )

    created = await create_competitor(comp_payload, db=db)
    return {"status": "created", "competitor_id": created.id, "competitor": created}

@router.post("/publish-test-article")
async def trigger_demo_publish():
    """
    Triggers the controlled demo site to publish a brand new test article.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(f"{settings.DEMO_SITE_URL}/api/publish")
            if resp.status_code == 200:
                return resp.json()
            return {"error": f"Demo site returned status {resp.status_code}"}
    except Exception as e:
        return {"error": f"Could not reach demo site at {settings.DEMO_SITE_URL}: {str(e)}"}
