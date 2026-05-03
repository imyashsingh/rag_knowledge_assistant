from typing import Optional
from sqlalchemy.orm import Session
from app.db.models.user import User
from app.db.models.workspace import Workspace
from app.db.repositories.user_repo import UserRepository
from app.db.repositories.workspace_repo import WorkspaceRepository
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, verify_refresh_token
from app.core.token_store import store_refresh_token, get_refresh_token, delete_refresh_token
from app.schemas.user import UserCreate, UserLogin
from app.schemas.auth import TokenResponse


def register_user(user_data: UserCreate, db: Session) -> TokenResponse:
    try:
        workspace_repo = WorkspaceRepository(db)
        user_repo = UserRepository(db)

        # Create workspace if it doesn't exist
        workspace = workspace_repo.get_by_name(user_data.workspace_name)
        if not workspace:
            workspace = workspace_repo.create_workspace(
                user_data.workspace_name)

        # Check if user already exists in this workspace
        existing_user = user_repo.get_by_email_and_workspace(
            user_data.email, workspace.id)
        if existing_user:
            raise ValueError("User already exists in this workspace")

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

        # Store refresh token in Redis
        store_refresh_token(user.id, refresh_token)

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
        user_repo = UserRepository(db)

        # Find user by email (we'll search across all workspaces for now)
        user = user_repo.get_by_email(user_data.email)

        if not user or not verify_password(user_data.password, user.password):
            raise ValueError("Invalid email or password")

        # Generate tokens
        access_token = create_access_token(
            {"user_id": user.id, "workspace_id": user.workspace_id})
        refresh_token = create_refresh_token(
            {"user_id": user.id, "workspace_id": user.workspace_id})

        # Store refresh token in Redis (replaces any existing token)
        store_refresh_token(user.id, refresh_token)

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

        # Check if refresh token exists in Redis
        stored_token = get_refresh_token(user_id)
        if not stored_token or stored_token != refresh_token:
            raise ValueError("Invalid or expired refresh token")

        # Generate new tokens
        new_access_token = create_access_token(
            {"user_id": user_id, "workspace_id": workspace_id})
        new_refresh_token = create_refresh_token(
            {"user_id": user_id, "workspace_id": workspace_id})

        # Rotate refresh token in Redis
        delete_refresh_token(user_id)
        store_refresh_token(user_id, new_refresh_token)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token
        )
    except Exception as e:
        raise ValueError(f"Token refresh failed: {str(e)}")


def logout_user(user_id: int) -> bool:
    try:
        delete_refresh_token(user_id)
        return True
    except Exception:
        return False
