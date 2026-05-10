from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.services.auth_service import register_user, login_user, refresh_token
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.schemas.auth import TokenResponse, RefreshTokenRequest
from app.api.deps import get_current_user, get_current_user_id
from app.db.repositories.user_repo import UserRepository
from app.db.repositories.workspace_repo import WorkspaceRepository
from app.db.session import get_db

router = APIRouter()


@router.post("/register", response_model=TokenResponse)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user and create workspace if needed"""
    try:
        return register_user(user_data, db)
    except ValueError as e:
        error_message = str(e)
        if "already exists" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": "USER_EXISTS",
                    "message": error_message,
                    "field": "email"
                }
            )
        elif "invalid email" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "INVALID_EMAIL",
                    "message": error_message,
                    "field": "email"
                }
            )
        elif "password" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "INVALID_PASSWORD",
                    "message": error_message,
                    "field": "password"
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "VALIDATION_ERROR",
                    "message": error_message
                }
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "REGISTRATION_FAILED",
                "message": "Registration failed. Please try again.",
                "details": str(e) if str(e) != "Registration failed: " else None
            }
        )


@router.post("/login", response_model=TokenResponse)
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    """Login user and return tokens"""
    try:
        return login_user(user_data, db)
    except ValueError as e:
        error_message = str(e)
        if "no account found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "USER_NOT_FOUND",
                    "message": error_message,
                    "field": "email"
                }
            )
        elif "incorrect password" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "INVALID_CREDENTIALS",
                    "message": error_message,
                    "field": "password"
                }
            )
        elif "invalid email" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "INVALID_EMAIL",
                    "message": error_message,
                    "field": "email"
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "LOGIN_FAILED",
                    "message": error_message
                }
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "LOGIN_FAILED",
                "message": "Login failed. Please try again.",
                "details": str(e) if str(e) != "Login failed: " else None
            }
        )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token_endpoint(token_data: RefreshTokenRequest):
    """Refresh access token using refresh token"""
    try:
        return refresh_token(token_data.refresh_token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed. Please login again."
        )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user information"""
    try:
        user_id = current_user.get("user_id")
        user_repo = UserRepository(db)
        user = user_repo.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "USER_NOT_FOUND",
                    "message": "User not found",
                    "field": "user_id"
                }
            )

        return UserResponse(
            id=user.id,
            email=user.email,
            workspace_id=user.workspace_id,
            created_at=user.created_at
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "USER_INFO_FAILED",
                "message": "Failed to get user info",
                "details": str(e)
            }
        )


@router.post("/switch-workspace")
def switch_workspace(
    workspace_data: dict,
    current_user: dict = Depends(get_current_user),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Switch user to a different workspace"""
    try:
        user_repo = UserRepository(db)
        workspace_repo = WorkspaceRepository(db)

        # Extract workspace_id from request body
        workspace_id = workspace_data.get('workspace_id')
        if not workspace_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "MISSING_WORKSPACE_ID",
                    "message": "workspace_id is required in request body",
                    "field": "workspace_id"
                }
            )

        # Verify workspace exists and user owns it
        workspace = workspace_repo.get_by_id(workspace_id)
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "WORKSPACE_NOT_FOUND",
                    "message": f"Workspace with ID {workspace_id} not found",
                    "field": "workspace_id"
                }
            )

        # Ensure user owns the workspace
        if workspace.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "WORKSPACE_ACCESS_DENIED",
                    "message": "You don't have permission to access this workspace",
                    "field": "workspace_id"
                }
            )

        # Update user's current workspace
        user_repo.update(user_id, workspace_id=workspace_id)

        # Generate new tokens with updated workspace_id
        from app.core.security import create_access_token, create_refresh_token
        access_token = create_access_token(
            {"user_id": user_id, "workspace_id": workspace_id})
        refresh_token = create_refresh_token(
            {"user_id": user_id, "workspace_id": workspace_id})

        return {
            "message": f"Successfully switched to workspace '{workspace.name}'",
            "workspace_id": workspace_id,
            "workspace_name": workspace.name,
            "access_token": access_token,
            "refresh_token": refresh_token
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "WORKSPACE_SWITCH_FAILED",
                "message": "Failed to switch workspace",
                "details": str(e)
            }
        )
