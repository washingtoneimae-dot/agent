from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False, index=True)
    score = Column(Integer, nullable=False)
    review_text = Column(Text)
    agent_used = Column(String(50))
    use_case = Column(String(50))
    synthesis_rounds = Column(String(10))
    paired_file_ids = Column(String(255))
    verified_download = Column(Boolean, default=False)
    user = relationship("User", backref="ratings")
    file = relationship("File", backref="ratings")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
