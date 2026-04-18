"""Test helper functions for the pet insurance domain."""
import uuid
from datetime import datetime, timezone

import bcrypt

from src.auth import sign_access_token
from src.store import store


def create_user(email: str, password: str, first_name: str, last_name: str, role: str) -> dict:
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user_id = str(uuid.uuid4())
    now = datetime.now(tz=timezone.utc).isoformat()
    user = {
        "id": user_id,
        "email": email,
        "password": hashed,
        "firstName": first_name,
        "lastName": last_name,
        "role": role,
        "createdAt": now,
    }
    store["users"][user_id] = user
    return user


def token_for_user(user: dict) -> str:
    return sign_access_token({"sub": user["id"], "email": user["email"], "role": user["role"]})


def create_pet_owner_token(email: str | None = None) -> dict:
    email = email or f"owner-{uuid.uuid4()}@test.com"
    user = create_user(email, "password123", "Pet", "Owner", "pet_owner")
    return {"token": token_for_user(user), "user": user}


def create_agent_token(email: str | None = None) -> dict:
    email = email or f"agent-{uuid.uuid4()}@test.com"
    user = create_user(email, "password123", "Insurance", "Agent", "agent")
    return {"token": token_for_user(user), "user": user}


def seed_pet(pet_owner_id: str, **overrides) -> dict:
    now = datetime.now(tz=timezone.utc).isoformat()
    pet = {
        "id": str(uuid.uuid4()),
        "name": "Buddy",
        "species": "dog",
        "breed": "Labrador",
        "dateOfBirth": "2020-03-15",
        "petOwnerId": pet_owner_id,
        "createdAt": now,
        "updatedAt": now,
        **overrides,
    }
    store["pets"][pet["id"]] = pet
    return pet


def seed_claim(pet_id: str, pet_owner_id: str, **overrides) -> dict:
    now = datetime.now(tz=timezone.utc).isoformat()
    claim = {
        "id": str(uuid.uuid4()),
        "petId": pet_id,
        "petOwnerId": pet_owner_id,
        "amount": 250.00,
        "description": "Routine check-up and vaccinations",
        "status": "pending",
        "createdAt": now,
        "updatedAt": now,
        **overrides,
    }
    store["claims"][claim["id"]] = claim
    return claim


def auth_header(token: str) -> dict:
    """Return an Authorization header dict with a bearer token."""
    scheme = "Bearer"
    return {"Authorization": f"{scheme} {token}"}
