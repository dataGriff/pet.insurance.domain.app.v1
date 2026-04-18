"""Auth routes — register, login, refresh token, logout."""
import uuid
from datetime import datetime, timezone

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, Response

from src.auth import (
    ACCESS_TOKEN_EXPIRES_IN,
    sign_access_token,
    sign_refresh_token,
    verify_token,
    JWTError,
)
from src.middleware.authenticate import authenticate
from src.models import AuthResponse, LoginRequest, RefreshRequest, RegisterRequest
from src.store import store

router = APIRouter()


@router.post("/auth/register", status_code=201, response_model=AuthResponse)
async def register(body: RegisterRequest):
    existing = next((u for u in store["users"].values() if u["email"] == body.email), None)
    if existing:
        raise HTTPException(
            status_code=409,
            detail={"code": "DUPLICATE_EMAIL", "message": "A user with this email address already exists."},
        )

    hashed = bcrypt.hashpw(body.password.encode(), bcrypt.gensalt()).decode()
    user_id = str(uuid.uuid4())
    now = datetime.now(tz=timezone.utc).isoformat()

    user = {
        "id": user_id,
        "email": str(body.email),
        "password": hashed,
        "firstName": body.firstName,
        "lastName": body.lastName,
        "role": body.role.value,
        "createdAt": now,
    }
    store["users"][user_id] = user

    payload = {"sub": user_id, "email": str(body.email), "role": body.role.value}
    access_token = sign_access_token(payload)
    refresh_token = sign_refresh_token(payload)

    return {
        "accessToken": access_token,
        "refreshToken": refresh_token,
        "expiresIn": ACCESS_TOKEN_EXPIRES_IN,
        "user": {
            "id": user_id,
            "email": str(body.email),
            "firstName": body.firstName,
            "lastName": body.lastName,
            "role": body.role.value,
        },
    }


@router.post("/auth/login", status_code=200, response_model=AuthResponse)
async def login(body: LoginRequest):
    user = next((u for u in store["users"].values() if u["email"] == str(body.email)), None)
    if not user:
        raise HTTPException(
            status_code=401,
            detail={"code": "INVALID_CREDENTIALS", "message": "The email or password provided is incorrect."},
        )
    if not bcrypt.checkpw(body.password.encode(), user["password"].encode()):
        raise HTTPException(
            status_code=401,
            detail={"code": "INVALID_CREDENTIALS", "message": "The email or password provided is incorrect."},
        )

    payload = {"sub": user["id"], "email": user["email"], "role": user["role"]}
    access_token = sign_access_token(payload)
    refresh_token = sign_refresh_token(payload)

    return {
        "accessToken": access_token,
        "refreshToken": refresh_token,
        "expiresIn": ACCESS_TOKEN_EXPIRES_IN,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "firstName": user["firstName"],
            "lastName": user["lastName"],
            "role": user["role"],
        },
    }


@router.post("/auth/logout", status_code=204)
async def logout(current_user: dict = Depends(authenticate)):
    return Response(status_code=204)


@router.post("/auth/refresh", status_code=200, response_model=AuthResponse)
async def refresh_token(body: RefreshRequest):
    try:
        decoded = verify_token(body.refreshToken)
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail={"code": "AUTHENTICATION_REQUIRED", "message": "Invalid or expired refresh token."},
        )

    user = store["users"].get(decoded.get("sub"))
    if not user:
        raise HTTPException(
            status_code=401,
            detail={"code": "AUTHENTICATION_REQUIRED", "message": "User not found."},
        )

    payload = {"sub": user["id"], "email": user["email"], "role": user["role"]}
    new_access_token = sign_access_token(payload)
    new_refresh_token = sign_refresh_token(payload)

    return {
        "accessToken": new_access_token,
        "refreshToken": new_refresh_token,
        "expiresIn": ACCESS_TOKEN_EXPIRES_IN,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "firstName": user["firstName"],
            "lastName": user["lastName"],
            "role": user["role"],
        },
    }
