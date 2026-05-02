from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext
from app.config import settings

pwd = CryptContext(schemes=["bcrypt"])


def hash_password(password: str) -> str:
    return pwd.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd.verify(password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + timedelta(minutes=15)
    to_encode["type"] = "access"
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + timedelta(days=7)
    to_encode["type"] = "refresh"
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")


def verify_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        if payload.get("type") != "access":
            raise JWTError("Invalid token type")
        return payload
    except JWTError:
        raise JWTError("Invalid access token")


def verify_refresh_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        if payload.get("type") != "refresh":
            raise JWTError("Invalid token type")
        return payload
    except JWTError:
        raise JWTError("Invalid refresh token")


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    except JWTError as e:
        raise JWTError(f"Token decode failed: {str(e)}")
