from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float
from pgvector.sqlalchemy import VECTOR
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Chunk(Base):
    __tablename__ = "chunks"
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    embedding = Column(VECTOR(384), nullable=False)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)  # Position in document
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    workspace = relationship("Workspace", back_populates="chunks")
    document = relationship("Document", back_populates="chunks")
