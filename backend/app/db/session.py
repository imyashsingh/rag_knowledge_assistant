from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
import os

# Create engine with connection pooling for production
engine = create_engine(
    settings.DB_URL,
    pool_size=10,          # Number of connections to keep open
    max_overflow=20,       # Allow 20 additional connections
    pool_pre_ping=True,    # Verify connections before use
    pool_recycle=3600,     # Recycle connections every hour
    # SQL logging in development
    echo=os.getenv("DEBUG", "false").lower() == "true"
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Dependency function to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
