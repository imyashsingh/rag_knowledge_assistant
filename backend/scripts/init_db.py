#!/usr/bin/env python3
"""
Database initialization script for DocuMind backend
"""

import os
import sys
from pathlib import Path

# Add app directory to Python path
app_dir = Path(__file__).parent.parent
sys.path.insert(0, str(app_dir))

from sqlalchemy import text
from app.db.session import engine
from app.db.base import Base
from app.utils.logger import setup_logging, get_logger


def setup_database():
    """Initialize database with tables and extensions"""
    logger = get_logger(__name__)
    
    try:
        logger.info("Starting database initialization...")
        
        # Create all tables
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Setup pgvector extension and indexes
        logger.info("Setting up pgvector extension and indexes...")
        with engine.connect() as conn:
            # Create pgvector extension
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            
            # Create optimized vector index
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_chunks_embedding
                ON chunks USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100)
            """))
            
            conn.commit()
        
        logger.info("pgvector extension and indexes setup complete")
        
        # Verify database setup
        logger.info("Verifying database setup...")
        with engine.connect() as conn:
            # Check pgvector extension
            result = conn.execute(text("SELECT 1 FROM pg_extension WHERE extname = 'vector'"))
            if not result.fetchone():
                raise Exception("pgvector extension not found")
            
            # Check tables exist
            tables = ['workspaces', 'users', 'documents', 'chunks']
            for table in tables:
                result = conn.execute(text(f"SELECT 1 FROM information_schema.tables WHERE table_name = '{table}'"))
                if not result.fetchone():
                    raise Exception(f"Table '{table}' not found")
        
        logger.info("Database verification successful")
        logger.info("Database initialization completed successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        return False


def check_database_connection():
    """Check database connection"""
    logger = get_logger(__name__)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        logger.info("Database connection successful")
        return True
        
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False


def reset_database():
    """Reset database (drop and recreate all tables) - DANGEROUS!"""
    logger = get_logger(__name__)
    
    # Safety check
    if os.getenv("ENVIRONMENT") == "production":
        logger.error("Database reset not allowed in production environment")
        return False
    
    response = input("WARNING: This will delete all data. Are you sure? (yes/no): ")
    if response.lower() != "yes":
        logger.info("Database reset cancelled")
        return False
    
    try:
        logger.info("Resetting database...")
        
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        logger.info("All tables dropped")
        
        # Recreate everything
        setup_database()
        
        logger.info("Database reset completed")
        return True
        
    except Exception as e:
        logger.error(f"Database reset failed: {str(e)}")
        return False


if __name__ == "__main__":
    # Setup logging
    setup_logging(log_level="INFO")
    
    logger = get_logger(__name__)
    logger.info("Database initialization script started")
    
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "check":
            success = check_database_connection()
        elif command == "reset":
            success = reset_database()
        elif command == "init":
            success = setup_database()
        else:
            logger.error(f"Unknown command: {command}")
            logger.info("Available commands: init, check, reset")
            sys.exit(1)
    else:
        # Default: setup database
        success = setup_database()
    
    if success:
        logger.info("Script completed successfully")
        sys.exit(0)
    else:
        logger.error("Script failed")
        sys.exit(1)
