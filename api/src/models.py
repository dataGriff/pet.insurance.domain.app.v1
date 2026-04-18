"""Pydantic models for request bodies and response shapes."""
from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr


class Role(str, Enum):
    contributor = "contributor"
    viewer = "viewer"


class ItemStatus(str, Enum):
    active = "active"
    archived = "archived"


# ---------------------------------------------------------------------------
# Auth request/response models
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    firstName: str
    lastName: str
    role: Role


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refreshToken: str


class UserSummary(BaseModel):
    id: str
    email: str
    firstName: str
    lastName: str
    role: Role


class AuthResponse(BaseModel):
    accessToken: str
    refreshToken: str
    expiresIn: int
    user: UserSummary


# ---------------------------------------------------------------------------
# Item request/response models
# ---------------------------------------------------------------------------

class Item(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    status: ItemStatus
    contributorId: str
    createdAt: str
    updatedAt: str


class Pagination(BaseModel):
    page: int
    pageSize: int
    total: int


class ItemList(BaseModel):
    data: List[Item]
    pagination: Pagination


class CreateItemRequest(BaseModel):
    name: str
    description: Optional[str] = None


class UpdateItemRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ItemStatus] = None


# ---------------------------------------------------------------------------
# Error models
# ---------------------------------------------------------------------------

class ErrorResponse(BaseModel):
    code: str
    message: str
