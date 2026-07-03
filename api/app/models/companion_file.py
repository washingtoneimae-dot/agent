from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class CompanionFile(Base):
    __tablename__ = "companion_files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False, index=True)
    companion_file_id = Column(Integer, ForeignKey("files.id"), nullable=False, index=True)
    pair_strength = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
