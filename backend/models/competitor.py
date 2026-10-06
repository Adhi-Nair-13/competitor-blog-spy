from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from backend.database import Base

class Competitor(Base):
    __tablename__ = "competitors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    website_url = Column(String(1024), nullable=False)
    blog_url = Column(String(1024), nullable=True)
    rss_url = Column(String(1024), nullable=True)
    sitemap_url = Column(String(1024), nullable=True)
    monitoring_enabled = Column(Boolean, default=True, nullable=False)
    monitoring_status = Column(String(50), default="ONLINE", nullable=False)  # ONLINE, OFFLINE, CHECKING, ERROR, DISABLED
    selected_strategy = Column(String(100), default="Automatic", nullable=False)  # RSS, Sitemap, Direct Page, RSS + Sitemap
    last_checked_at = Column(DateTime(timezone=True), nullable=True)
    last_successful_detection_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    articles = relationship("Article", back_populates="competitor", cascade="all, delete-orphan", order_by="desc(Article.detected_at)")
    monitoring_checks = relationship("MonitoringCheck", back_populates="competitor", cascade="all, delete-orphan", order_by="desc(MonitoringCheck.started_at)")
    configuration = relationship("MonitoringConfiguration", back_populates="competitor", uselist=False, cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="competitor", cascade="all, delete-orphan", order_by="desc(Notification.created_at)")
