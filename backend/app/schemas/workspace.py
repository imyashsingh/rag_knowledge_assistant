from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class WorkspaceCreate(BaseModel):
    name: str


class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None


class WorkspaceResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


class WorkspaceWithUsers(BaseModel):
    id: int
    name: str
    created_at: datetime
    users: List[dict]  # Simplified user info

    class Config:
        from_attributes = True


class WorkspaceStats(BaseModel):
    id: int
    name: str
    document_count: int
    user_count: int
    chat_count: int
    session_count: int
    created_at: datetime
