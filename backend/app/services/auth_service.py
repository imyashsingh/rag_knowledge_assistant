from typing import Optional
from sqlalchemy.orm import Session
from app.db.models.user import User
from app.db.models.workspace import Workspace
from app.db.repositories.user_repo import UserRepository
from app.db.repositories.workspace_repo import WorkspaceRepository
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, verify_refresh_token
from app.schemas.user import UserCreate, UserLogin
from app.schemas.auth import TokenResponse


def register_user(user_data: UserCreate, db: Session) -> TokenResponse:
    try:
        # Validate input data
        if not user_data.email or '@' not in user_data.email:
            raise ValueError("Invalid email address format")

        if not user_data.password or len(user_data.password) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if not user_data.name or len(user_data.name.strip()) < 2:
            raise ValueError("Name must be at least 2 characters long")

        workspace_repo = WorkspaceRepository(db)
        user_repo = UserRepository(db)

        # Normalize workspace name - fall back to "Default Workspace" if blank
        workspace_name = (
            user_data.workspace_name or "").strip() or "Default Workspace"

        # Create workspace if it doesn't exist
        workspace = workspace_repo.get_by_name(workspace_name)
        if not workspace:
            workspace = workspace_repo.create_workspace(workspace_name)

        # Check if user already exists in this workspace
        existing_user = user_repo.get_by_email_and_workspace(
            user_data.email, workspace.id)
        if existing_user:
            raise ValueError(
                f"User with email '{user_data.email}' already exists in workspace '{user_data.workspace_name}'")

        # Create user
        user = user_repo.create_user(
            email=user_data.email,
            name=user_data.name,
            password=hash_password(user_data.password),
            workspace_id=workspace.id
        )

        # Generate tokens
        access_token = create_access_token(
            {"user_id": user.id, "workspace_id": workspace.id})
        refresh_token = create_refresh_token(
            {"user_id": user.id, "workspace_id": workspace.id})

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Registration failed: {str(e)}")


def login_user(user_data: UserLogin, db: Session) -> TokenResponse:
    try:
        # Validate input data
        if not user_data.email or '@' not in user_data.email:
            raise ValueError("Invalid email address format")

        if not user_data.password:
            raise ValueError("Password is required")

        user_repo = UserRepository(db)

        # Find user by email (we'll search across all workspaces for now)
        user = user_repo.get_by_email(user_data.email)

        if not user:
            raise ValueError(
                f"No account found with email '{user_data.email}'")

        if not verify_password(user_data.password, user.password):
            raise ValueError("Incorrect password")

        # Generate tokens
        access_token = create_access_token(
            {"user_id": user.id, "workspace_id": user.workspace_id})
        refresh_token = create_refresh_token(
            {"user_id": user.id, "workspace_id": user.workspace_id})

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Login failed: {str(e)}")


def refresh_token(refresh_token: str) -> TokenResponse:
    try:
        # Verify refresh token and get payload
        payload = verify_refresh_token(refresh_token)
        user_id = payload.get("user_id")
        workspace_id = payload.get("workspace_id")

        # Generate new tokens
        new_access_token = create_access_token(
            {"user_id": user_id, "workspace_id": workspace_id})
        new_refresh_token = create_refresh_token(
            {"user_id": user_id, "workspace_id": workspace_id})

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token
        )
    except Exception as e:
        raise ValueError(f"Token refresh failed: {str(e)}")
