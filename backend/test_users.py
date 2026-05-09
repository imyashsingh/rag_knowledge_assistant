import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models.user import User

DB_URL = "postgresql://postgres:r0PBehbu45KxnQJC@db.pczjkkvmrvuphixwnqml.supabase.co:5432/postgres"
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

users = db.query(User).all()
for u in users:
    print(f"ID: {u.id}, Email: {u.email}, Workspace: {u.workspace_id}")
