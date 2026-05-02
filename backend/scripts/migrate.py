#!/usr/bin/env python3
"""
Database migration script for DocuMind backend
"""

import os
import sys
from pathlib import Path

# Add app directory to Python path
app_dir = Path(__file__).parent.parent
sys.path.insert(0, str(app_dir))

from alembic.config import Config
from alembic import command
from app.utils.logger import setup_logging, get_logger


def run_migrations():
    """Run database migrations using Alembic"""
    logger = get_logger(__name__)
    
    try:
        logger.info("Running database migrations...")
        
        # Get Alembic configuration
        alembic_cfg = Config("alembic.ini")
        
        # Run migrations
        command.upgrade(alembic_cfg, "head")
        
        logger.info("Database migrations completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        return False


def create_migration(message: str):
    """Create a new migration"""
    logger = get_logger(__name__)
    
    try:
        logger.info(f"Creating migration: {message}")
        
        alembic_cfg = Config("alembic.ini")
        command.revision(alembic_cfg, autogenerate=True, message=message)
        
        logger.info("Migration created successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Migration creation failed: {str(e)}")
        return False


def get_migration_status():
    """Get current migration status"""
    logger = get_logger(__name__)
    
    try:
        alembic_cfg = Config("alembic.ini")
        
        # Get current revision
        current = command.current(alembic_cfg)
        
        # Get head revision
        head = command.heads(alembic_cfg)
        
        logger.info(f"Current revision: {current}")
        logger.info(f"Head revision: {head}")
        
        if current == head:
            logger.info("Database is up to date")
        else:
            logger.info("Database needs migration")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to get migration status: {str(e)}")
        return False


def downgrade_migration(revision: str):
    """Downgrade to specific revision"""
    logger = get_logger(__name__)
    
    # Safety check
    if os.getenv("ENVIRONMENT") == "production":
        logger.error("Downgrade not allowed in production environment")
        return False
    
    try:
        logger.info(f"Downgrading to revision: {revision}")
        
        alembic_cfg = Config("alembic.ini")
        command.downgrade(alembic_cfg, revision)
        
        logger.info("Downgrade completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Downgrade failed: {str(e)}")
        return False


if __name__ == "__main__":
    # Setup logging
    setup_logging(log_level="INFO")
    
    logger = get_logger(__name__)
    logger.info("Migration script started")
    
    # Check command line arguments
    if len(sys.argv) > 1:
        command_arg = sys.argv[1].lower()
        
        if command_arg == "upgrade":
            success = run_migrations()
        elif command_arg == "status":
            success = get_migration_status()
        elif command_arg == "create":
            if len(sys.argv) < 3:
                logger.error("Migration message required for create command")
                logger.info("Usage: python migrate.py create \"migration message\"")
                sys.exit(1)
            
            message = " ".join(sys.argv[2:])
            success = create_migration(message)
        elif command_arg == "downgrade":
            if len(sys.argv) < 3:
                logger.error("Revision required for downgrade command")
                logger.info("Usage: python migrate.py downgrade <revision>")
                sys.exit(1)
            
            revision = sys.argv[2]
            success = downgrade_migration(revision)
        else:
            logger.error(f"Unknown command: {command_arg}")
            logger.info("Available commands: upgrade, status, create, downgrade")
            sys.exit(1)
    else:
        # Default: run migrations
        success = run_migrations()
    
    if success:
        logger.info("Script completed successfully")
        sys.exit(0)
    else:
        logger.error("Script failed")
        sys.exit(1)
