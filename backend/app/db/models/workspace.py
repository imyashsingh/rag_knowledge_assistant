from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Workspace(Base):
    __tablename__ = "workspaces"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    users = relationship("User", back_populates="workspace")
    documents = relationship("Document", back_populates="workspace", cascade="all, delete-orphan")
    chunks = relationship("Chunk", back_populates="workspace", cascade="all, delete-orphan")
