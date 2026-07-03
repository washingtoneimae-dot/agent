from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class FileCategory(str, enum.Enum):
    DATA_ANALYSIS = "data_analysis"
    MARKETING = "marketing"
    CODING = "coding"
    RESEARCH = "research"
    CONTENT = "content"
    OTHER = "other"


class FileStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    FLAGGED = "flagged"
    REMOVED = "removed"
    ARCHIVED = "archived"


class FileProductTier(str, enum.Enum):
    SKILL_CREATION_FILE = "skill_creation_file"
    COMPLETE_SKILL = "complete_skill"
    WORKFLOW_TEMPLATE = "workflow_template"


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    contributor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("files.id"), nullable=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(Enum(FileCategory), nullable=False, index=True)
    product_tier = Column(Enum(FileProductTier), nullable=False, default=FileProductTier.SKILL_CREATION_FILE)
    tags = Column(String(500))
    download_count = Column(Integer, default=0)
    extraction_count = Column(Integer, default=0)
    children_count = Column(Integer, default=0)
    score = Column(Float, default=10.0, index=True)
    status = Column(Enum(FileStatus), default=FileStatus.PENDING)
    storage_path = Column(String(500))
    file_size = Column(Integer, default=0)
    original_filename = Column(String(255))
    contributor = relationship("User", backref="files")
    parent = relationship("File", remote_side="File.id", backref="children")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
