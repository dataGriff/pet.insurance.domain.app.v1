"""Test helper functions — equivalent to tests/helpers.js."""
import uuid
from datetime import datetime, timezone

import bcrypt
from fastapi.testclient import TestClient

from src.auth import sign_access_token
from src.main import app
from src.store import reset_store, store


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


def create_contributor_token(email: str | None = None) -> dict:
    email = email or f"contributor-{uuid.uuid4()}@test.com"
    user = create_user(email, "password123", "Test", "Contributor", "contributor")
    return {"token": token_for_user(user), "user": user}


def create_viewer_token(email: str | None = None) -> dict:
    email = email or f"viewer-{uuid.uuid4()}@test.com"
    user = create_user(email, "password123", "Test", "Viewer", "viewer")
    return {"token": token_for_user(user), "user": user}


def seed_item(contributor_id: str, **overrides) -> dict:
    now = datetime.now(tz=timezone.utc).isoformat()
    item = {
        "id": str(uuid.uuid4()),
        "name": "Sample Item",
        "description": "A sample item description.",
        "status": "active",
        "contributorId": contributor_id,
        "createdAt": now,
        "updatedAt": now,
        **overrides,
    }
    store["items"][item["id"]] = item
    return item
