from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DocumentBase(BaseModel):
    title: str
    filename: str


class DocumentCreate(DocumentBase):
    content_type: str


class DocumentResponse(DocumentBase):
    id: int
    content_type: str
    workspace_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
