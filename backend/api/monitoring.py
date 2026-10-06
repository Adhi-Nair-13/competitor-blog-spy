from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.database import get_db
from backend.models.monitoring_check import MonitoringCheck
from backend.models.competitor import Competitor
from backend.schemas.monitoring import MonitoringCheckResponse
from backend.services.monitoring_scheduler import monitoring_scheduler

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])

@router.get("/history", response_model=List[MonitoringCheckResponse])
def get_monitoring_history(
    competitor_id: Optional[int] = None,
    status: Optional[str] = None,
    detection_method: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(MonitoringCheck, Competitor.name).join(Competitor, MonitoringCheck.competitor_id == Competitor.id)

    if competitor_id:
        query = query.filter(MonitoringCheck.competitor_id == competitor_id)
    if status:
        query = query.filter(MonitoringCheck.status == status.upper())
    if detection_method:
        query = query.filter(MonitoringCheck.detection_method.ilike(f"%{detection_method}%"))

    checks = query.order_by(desc(MonitoringCheck.started_at)).offset(offset).limit(limit).all()

    results = []
    for check, comp_name in checks:
        item = MonitoringCheckResponse.model_validate(check)
        item.competitor_name = comp_name
        results.append(item)

    return results

@router.post("/run-all")
async def trigger_run_all():
    # Run scheduled check asynchronously in background
    import asyncio
    asyncio.create_task(monitoring_scheduler.run_scheduled_checks())
    return {"message": "Full monitoring check initiated across all active competitors."}
