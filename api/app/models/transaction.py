from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum


class TransactionType(str, enum.Enum):
    PURCHASE = "purchase"
    DOWNLOAD = "download"
    EARN = "earn"
    PAYOUT = "payout"
    ADMIN_CREDIT = "admin_credit"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=True)
    type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    balance_after = Column(Float, nullable=True)
    description = Column(String(255))
    reference_id = Column(String(100), unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
