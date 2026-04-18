"""JWT signing and verification utilities."""
import os
from datetime import datetime, timezone, timedelta

from jose import jwt, JWTError, ExpiredSignatureError

JWT_SECRET = os.environ.get("JWT_SECRET", "test-secret")
ACCESS_TOKEN_EXPIRES_IN = 3600  # seconds
_REFRESH_TOKEN_EXPIRES_IN = 7 * 24 * 3600  # 7 days


def sign_access_token(payload: dict) -> str:
    data = payload.copy()
    data["exp"] = datetime.now(tz=timezone.utc) + timedelta(seconds=ACCESS_TOKEN_EXPIRES_IN)
    return jwt.encode(data, JWT_SECRET, algorithm="HS256")


def sign_refresh_token(payload: dict) -> str:
    data = payload.copy()
    data["exp"] = datetime.now(tz=timezone.utc) + timedelta(seconds=_REFRESH_TOKEN_EXPIRES_IN)
    return jwt.encode(data, JWT_SECRET, algorithm="HS256")


def verify_token(token: str) -> dict:
    """Decode and verify a JWT. Raises jose.JWTError or jose.ExpiredSignatureError."""
    return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])


__all__ = [
    "sign_access_token",
    "sign_refresh_token",
    "verify_token",
    "ACCESS_TOKEN_EXPIRES_IN",
    "JWTError",
    "ExpiredSignatureError",
]
