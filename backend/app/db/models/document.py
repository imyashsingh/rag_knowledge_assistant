from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    workspace = relationship("Workspace", back_populates="documents")
    chunks = relationship("Chunk", back_populates="document",
                          cascade="all, delete-orphan")
