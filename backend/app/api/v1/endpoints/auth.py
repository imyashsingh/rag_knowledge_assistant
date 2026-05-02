from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.services.auth_service import register_user, login_user, refresh_token, logout_user
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.schemas.auth import TokenResponse, RefreshTokenRequest
from app.api.deps import get_current_user
from app.db.repositories.user_repo import UserRepository
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again."
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


@router.post("/logout")
def logout(current_user: dict = Depends(get_current_user)):
    """Logout user and invalidate refresh token"""
    try:
        user_id = current_user.get("user_id")
        success = logout_user(user_id)

        if success:
            return {"message": "Successfully logged out"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Logout failed"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
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
                detail="User not found"
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
            detail="Failed to get user information"
        )
