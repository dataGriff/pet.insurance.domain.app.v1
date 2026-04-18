"""JWT authentication dependency and requireRole helper."""
from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.auth import verify_token, JWTError, ExpiredSignatureError

_bearer_scheme = HTTPBearer(auto_error=False)


def authenticate(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> dict:
    """FastAPI dependency that validates the Bearer token and returns the decoded payload."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "AUTHENTICATION_REQUIRED", "message": "A valid bearer token is required to access this resource."},
        )
    token = credentials.credentials
    try:
        payload = verify_token(token)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "TOKEN_EXPIRED", "message": "The access token has expired. Please refresh your session."},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "AUTHENTICATION_REQUIRED", "message": "A valid bearer token is required to access this resource."},
        )
    return payload


def require_role(role: str) -> Callable[[dict], dict]:
    """Returns a FastAPI dependency that checks the user has the given role."""
    def _check(user: dict = Depends(authenticate)) -> dict:
        if user.get("role") != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN", "message": "Your role does not have permission to perform this action."},
            )
        return user
    return _check
