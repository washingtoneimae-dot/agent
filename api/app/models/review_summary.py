from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.database import Base


class ReviewSummary(Base):
    __tablename__ = "review_summaries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False, unique=True, index=True)
    summary_json = Column(JSON, nullable=False)
    dimensions_json = Column(JSON, nullable=True)
    total_reviews = Column(Integer, default=0)
    avg_score = Column(Float, default=0.0)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
