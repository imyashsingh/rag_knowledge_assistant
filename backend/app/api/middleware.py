from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from app.core.security import verify_access_token
import time
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()


async def log_requests(request: Request, call_next):
    """Log request timing and basic info"""
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.4f}s"
    )

    return response


async def jwt_auth_middleware(request: Request, call_next):
    """JWT Authentication Middleware"""
    # Skip auth for certain paths
    skip_paths = ["/api/v1/register", "/api/v1/login",
                  "/api/v1/health", "/docs", "/redoc"]
    if any(request.url.path.startswith(path) for path in skip_paths):
        return await call_next(request)

    # Check for Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_header.split(" ")[1]

    try:
        # Verify token
        payload = verify_access_token(token)

        # Add user info to request state
        request.state.user_id = payload.get("user_id")
        request.state.workspace_id = payload.get("workspace_id")

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return await call_next(request)
