from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class MonitoringConfiguration(Base):
    __tablename__ = "monitoring_configurations"

    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    rss_available = Column(Boolean, default=False, nullable=False)
    rss_url = Column(String(1024), nullable=True)
    atom_available = Column(Boolean, default=False, nullable=False)
    
    sitemap_available = Column(Boolean, default=False, nullable=False)
    sitemap_url = Column(String(1024), nullable=True)
    sitemap_index = Column(Boolean, default=False, nullable=False)
    
    blog_url = Column(String(1024), nullable=True)
    article_pattern = Column(String(255), nullable=True)
    
    publication_date_available = Column(Boolean, default=False, nullable=False)
    structured_metadata_available = Column(Boolean, default=False, nullable=False)
    canonical_url_available = Column(Boolean, default=False, nullable=False)
    
    selected_strategy = Column(String(100), default="None", nullable=False)
    analysis_timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    competitor = relationship("Competitor", back_populates="configuration")
