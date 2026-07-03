from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum


class PayoutStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ContributorPayout(Base):
    __tablename__ = "contributor_payouts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    contributor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    period = Column(String(20), nullable=False)
    status = Column(Enum(PayoutStatus), default=PayoutStatus.PENDING)
    payment_method = Column(String(50))
    payment_reference = Column(String(255))
    notes = Column(String(500))
    processed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
