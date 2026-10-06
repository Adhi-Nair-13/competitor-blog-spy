from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(512), nullable=False, index=True)
    content = Column(Text, nullable=True)
    author = Column(String(255), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True, index=True)
    detected_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    detection_delay_seconds = Column(Float, nullable=True)  # detected_at - published_at in seconds
    detection_method = Column(String(50), nullable=False)  # RSS, Sitemap, Direct Page
    canonical_url = Column(String(1024), unique=True, index=True, nullable=False)
    source_url = Column(String(1024), nullable=False)
    meta_description = Column(Text, nullable=True)
    featured_image = Column(String(1024), nullable=True)
    categories = Column(Text, nullable=True)  # Comma separated or JSON string
    tags = Column(Text, nullable=True)        # Comma separated or JSON string
    relevant_links = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    competitor = relationship("Competitor", back_populates="articles")
