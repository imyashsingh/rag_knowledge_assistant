from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str
    workspace_name: Optional[str] = "Default Workspace"


class UserLogin(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    workspace_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
