from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class MonitoringCheck(Base):
    __tablename__ = "monitoring_checks"

    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id", ondelete="CASCADE"), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(50), nullable=False, default="SUCCESS")  # SUCCESS, FAILED, PARTIAL
    detection_method = Column(String(100), nullable=False)          # RSS, Sitemap, Direct Page, Combined
    articles_found = Column(Integer, default=0, nullable=False)
    new_articles_found = Column(Integer, default=0, nullable=False)
    response_time_ms = Column(Float, default=0.0, nullable=False)
    error_message = Column(Text, nullable=True)

    # Relationships
    competitor = relationship("Competitor", back_populates="monitoring_checks")
