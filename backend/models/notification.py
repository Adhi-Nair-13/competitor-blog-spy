from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id", ondelete="CASCADE"), nullable=False, index=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    detection_method = Column(String(50), nullable=False)
    detection_delay_seconds = Column(Float, nullable=True)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    competitor = relationship("Competitor", back_populates="notifications")
