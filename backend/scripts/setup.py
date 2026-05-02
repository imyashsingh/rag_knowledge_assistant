#!/usr/bin/env python3
"""
Complete setup script for DocuMind backend
"""

import os
import sys
import subprocess
from pathlib import Path

# Add app directory to Python path
app_dir = Path(__file__).parent.parent
sys.path.insert(0, str(app_dir))

from app.utils.logger import setup_logging, get_logger


def run_command(command: str, description: str) -> bool:
    """Run a command and return success status"""
    logger = get_logger(__name__)
    
    logger.info(f"Running: {description}")
    logger.info(f"Command: {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=app_dir
        )
        
        if result.returncode == 0:
            logger.info(f"✅ {description} completed successfully")
            if result.stdout:
                logger.debug(f"Output: {result.stdout}")
            return True
        else:
            logger.error(f"❌ {description} failed")
            if result.stderr:
                logger.error(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ {description} failed: {str(e)}")
        return False


def check_environment():
    """Check if required environment variables are set"""
    logger = get_logger(__name__)
    
    required_vars = ["DB_URL", "JWT_SECRET", "GROQ_API_KEY", "REDIS_HOST", "REDIS_PASSWORD"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.info("Please set these variables in your .env file")
        return False
    
    logger.info("✅ All required environment variables are set")
    return True


def setup_complete():
    """Run complete setup process"""
    logger = get_logger(__name__)
    
    logger.info("🚀 Starting DocuMind backend setup...")
    
    # Check environment
    if not check_environment():
        return False
    
    # Setup steps
    setup_steps = [
        ("python scripts/init_db.py init", "Database initialization"),
        ("python scripts/migrate.py upgrade", "Database migrations"),
        ("python scripts/create_admin.py interactive", "Create admin user"),
        ("python scripts/seed_data.py seed", "Seed sample data"),
        ("python scripts/health_check.py", "Health check"),
    ]
    
    success_count = 0
    
    for command, description in setup_steps:
        if run_command(command, description):
            success_count += 1
        else:
            logger.error(f"Setup failed at: {description}")
            logger.info("Please fix the error and run setup again")
            return False
    
    logger.info(f"🎉 Setup completed successfully! ({success_count}/{len(setup_steps)} steps)")
    
    # Next steps
    logger.info("\n📋 Next steps:")
    logger.info("1. Start the application: uvicorn app.main:app --reload")
    logger.info("2. Visit http://localhost:8000/docs for API documentation")
    logger.info("3. Login with your admin credentials")
    logger.info("4. Upload documents and start using the RAG system")
    
    return True


def quick_setup():
    """Quick setup without sample data"""
    logger = get_logger(__name__)
    
    logger.info("⚡ Starting quick setup...")
    
    # Check environment
    if not check_environment():
        return False
    
    # Essential setup steps only
    setup_steps = [
        ("python scripts/init_db.py init", "Database initialization"),
        ("python scripts/migrate.py upgrade", "Database migrations"),
        ("python scripts/create_admin.py interactive", "Create admin user"),
        ("python scripts/health_check.py", "Health check"),
    ]
    
    for command, description in setup_steps:
        if not run_command(command, description):
            logger.error(f"Quick setup failed at: {description}")
            return False
    
    logger.info("⚡ Quick setup completed successfully!")
    logger.info("Run 'python scripts/setup.py' for full setup with sample data")
    
    return True


def production_setup():
    """Production setup (without sample data or interactive prompts)"""
    logger = get_logger(__name__)
    
    # Check if we're in production environment
    if os.getenv("ENVIRONMENT") != "production":
        logger.warning("Not in production environment. Use 'production' ENVIRONMENT setting.")
        return False
    
    logger.info("🏭 Starting production setup...")
    
    # Check environment
    if not check_environment():
        return False
    
    # Production setup steps
    setup_steps = [
        ("python scripts/init_db.py init", "Database initialization"),
        ("python scripts/migrate.py upgrade", "Database migrations"),
        ("python scripts/health_check.py", "Health check"),
    ]
    
    for command, description in setup_steps:
        if not run_command(command, description):
            logger.error(f"Production setup failed at: {description}")
            return False
    
    logger.info("🏭 Production setup completed successfully!")
    logger.info("Create admin user manually: python scripts/create_admin.py <email> <password>")
    
    return True


if __name__ == "__main__":
    # Setup logging
    setup_logging(log_level="INFO")
    
    logger = get_logger(__name__)
    logger.info("Setup script started")
    
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "complete":
            success = setup_complete()
        elif command == "quick":
            success = quick_setup()
        elif command == "production":
            success = production_setup()
        elif command == "check":
            success = check_environment()
        else:
            logger.error(f"Unknown command: {command}")
            logger.info("Available commands: complete, quick, production, check")
            sys.exit(1)
    else:
        # Default: complete setup
        success = setup_complete()
    
    sys.exit(0 if success else 1)
