#!/usr/bin/env python3
"""
Create admin user script for DocuMind backend
"""

import os
import sys
import getpass
from pathlib import Path

# Add app directory to Python path
app_dir = Path(__file__).parent.parent
sys.path.insert(0, str(app_dir))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.repositories.workspace_repo import WorkspaceRepository
from app.db.repositories.user_repo import UserRepository
from app.core.security import hash_password
from app.utils.logger import setup_logging, get_logger


def create_admin_user(email: str, password: str, workspace_name: str = "Default Workspace"):
    """Create admin user with default workspace"""
    logger = get_logger(__name__)
    
    try:
        logger.info(f"Creating admin user: {email}")
        
        db = SessionLocal()
        try:
            # Initialize repositories
            workspace_repo = WorkspaceRepository(db)
            user_repo = UserRepository(db)
            
            # Check if user already exists
            existing_user = user_repo.get_by_email(email)
            if existing_user:
                logger.error(f"User with email {email} already exists")
                return False
            
            # Create or get workspace
            workspace = workspace_repo.get_by_name(workspace_name)
            if not workspace:
                workspace = workspace_repo.create_workspace(workspace_name)
                logger.info(f"Created workspace: {workspace_name}")
            
            # Create admin user
            user = user_repo.create_user(
                email=email,
                password=hash_password(password),
                workspace_id=workspace.id
            )
            
            logger.info(f"Admin user created successfully with ID: {user.id}")
            logger.info(f"Workspace ID: {workspace.id}")
            
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Failed to create admin user: {str(e)}")
        return False


def list_users():
    """List all users in the database"""
    logger = get_logger(__name__)
    
    try:
        db = SessionLocal()
        try:
            user_repo = UserRepository(db)
            users = user_repo.get_all()
            
            if not users:
                logger.info("No users found in database")
                return
            
            logger.info(f"Found {len(users)} users:")
            for user in users:
                logger.info(f"  - ID: {user.id}, Email: {user.email}, Workspace: {user.workspace_id}")
                
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Failed to list users: {str(e)}")


def interactive_create_admin():
    """Interactive admin user creation"""
    logger = get_logger(__name__)
    
    print("=== Create Admin User ===")
    
    # Get email
    while True:
        email = input("Enter admin email: ").strip()
        if not email:
            print("Email is required")
            continue
        
        if "@" not in email or "." not in email:
            print("Please enter a valid email address")
            continue
        
        break
    
    # Get password
    while True:
        password = getpass.getpass("Enter admin password: ")
        if not password:
            print("Password is required")
            continue
        
        if len(password) < 8:
            print("Password must be at least 8 characters long")
            continue
        
        confirm_password = getpass.getpass("Confirm password: ")
        if password != confirm_password:
            print("Passwords do not match")
            continue
        
        break
    
    # Get workspace name
    workspace_name = input("Enter workspace name (Default Workspace): ").strip()
    if not workspace_name:
        workspace_name = "Default Workspace"
    
    # Create user
    success = create_admin_user(email, password, workspace_name)
    
    if success:
        print(f"\n✅ Admin user '{email}' created successfully!")
        print(f"   Workspace: {workspace_name}")
        print(f"\nYou can now login with these credentials.")
    else:
        print(f"\n❌ Failed to create admin user")
        sys.exit(1)


if __name__ == "__main__":
    # Setup logging
    setup_logging(log_level="INFO")
    
    logger = get_logger(__name__)
    logger.info("Admin user creation script started")
    
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "list":
            list_users()
        elif command == "create":
            if len(sys.argv) >= 4:
                email = sys.argv[2]
                password = sys.argv[3]
                workspace_name = sys.argv[4] if len(sys.argv) > 4 else "Default Workspace"
                
                success = create_admin_user(email, password, workspace_name)
                if not success:
                    sys.exit(1)
            else:
                print("Usage: python create_admin.py create <email> <password> [workspace_name]")
                sys.exit(1)
        elif command == "interactive":
            interactive_create_admin()
        else:
            logger.error(f"Unknown command: {command}")
            logger.info("Available commands: list, create, interactive")
            sys.exit(1)
    else:
        # Default: interactive mode
        interactive_create_admin()
