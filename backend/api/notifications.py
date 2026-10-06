from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.database import get_db
from backend.models.notification import Notification
from backend.models.competitor import Competitor
from backend.schemas.monitoring import NotificationResponse
from backend.utils.date_helpers import format_detection_delay

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("", response_model=List[NotificationResponse])
def get_notifications(limit: int = Query(50, ge=1, le=100), db: Session = Depends(get_db)):
    notifs = (
        db.query(Notification, Competitor.name)
        .join(Competitor, Notification.competitor_id == Competitor.id)
        .order_by(desc(Notification.created_at))
        .limit(limit)
        .all()
    )

    results = []
    for n, comp_name in notifs:
        item = NotificationResponse.model_validate(n)
        item.competitor_name = comp_name
        item.detection_delay_formatted = format_detection_delay(n.detection_delay_seconds)
        results.append(item)

    return results

@router.get("/unread-count")
def get_unread_count(db: Session = Depends(get_db)):
    count = db.query(Notification).filter(Notification.is_read == False).count()
    return {"unread_count": count}

@router.put("/{id}/read")
def mark_as_read(id: int, db: Session = Depends(get_db)):
    notif = db.query(Notification).filter(Notification.id == id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    db.commit()
    return {"status": "success", "id": id, "is_read": True}

@router.post("/read-all")
def mark_all_read(db: Session = Depends(get_db)):
    db.query(Notification).filter(Notification.is_read == False).update({Notification.is_read: True})
    db.commit()
    return {"status": "success", "message": "All notifications marked as read"}

@router.delete("/{id}")
def delete_notification(id: int, db: Session = Depends(get_db)):
    notif = db.query(Notification).filter(Notification.id == id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    db.delete(notif)
    db.commit()
    return {"status": "success", "id": id}
