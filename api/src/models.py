"""Pydantic models for the pet insurance domain API."""
from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr


class Role(str, Enum):
    pet_owner = "pet_owner"
    agent = "agent"


class Species(str, Enum):
    dog = "dog"
    cat = "cat"
    rabbit = "rabbit"
    bird = "bird"
    other = "other"


class ClaimStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


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
# Pet request/response models
# ---------------------------------------------------------------------------

class Pet(BaseModel):
    id: str
    name: str
    species: Species
    breed: Optional[str] = None
    dateOfBirth: str
    petOwnerId: str
    createdAt: str
    updatedAt: str


class RegisterPetRequest(BaseModel):
    name: str
    species: Species
    breed: Optional[str] = None
    dateOfBirth: str


class EditPetRequest(BaseModel):
    name: Optional[str] = None
    breed: Optional[str] = None
    dateOfBirth: Optional[str] = None


# ---------------------------------------------------------------------------
# Claim request/response models
# ---------------------------------------------------------------------------

class Claim(BaseModel):
    id: str
    petId: str
    petOwnerId: str
    amount: float
    description: str
    status: ClaimStatus
    createdAt: str
    updatedAt: str


class Pagination(BaseModel):
    page: int
    pageSize: int
    total: int


class ClaimList(BaseModel):
    data: List[Claim]
    pagination: Pagination


class SubmitClaimRequest(BaseModel):
    petId: str
    amount: float
    description: str


# ---------------------------------------------------------------------------
# Error model
# ---------------------------------------------------------------------------

class ErrorResponse(BaseModel):
    code: str
    message: str
