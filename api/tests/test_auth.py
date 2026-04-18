"""Auth route tests."""
import pytest
from fastapi.testclient import TestClient

from src.main import app
from tests.helpers import auth_header


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


class TestRegister:
    def test_registers_a_new_pet_owner_and_returns_tokens(self, client):
        res = client.post("/v1/auth/register", json={
            "email": "owner@example.com",
            "password": "password123",
            "firstName": "Alice",
            "lastName": "Smith",
            "role": "pet_owner",
        })
        assert res.status_code == 201
        assert res.json()["accessToken"]
        assert res.json()["refreshToken"]
        assert res.json()["expiresIn"] == 3600
        assert res.json()["user"]["role"] == "pet_owner"

    def test_registers_a_new_agent(self, client):
        res = client.post("/v1/auth/register", json={
            "email": "agent@example.com",
            "password": "password123",
            "firstName": "Bob",
            "lastName": "Jones",
            "role": "agent",
        })
        assert res.status_code == 201
        assert res.json()["user"]["role"] == "agent"

    def test_returns_409_for_duplicate_email(self, client):
        payload = {
            "email": "dup@example.com",
            "password": "password123",
            "firstName": "A",
            "lastName": "B",
            "role": "pet_owner",
        }
        client.post("/v1/auth/register", json=payload)
        res = client.post("/v1/auth/register", json=payload)
        assert res.status_code == 409
        assert res.json()["code"] == "DUPLICATE_EMAIL"


class TestLogin:
    def test_logs_in_with_correct_credentials(self, client):
        client.post("/v1/auth/register", json={
            "email": "login@example.com",
            "password": "mypassword",
            "firstName": "L",
            "lastName": "U",
            "role": "pet_owner",
        })
        res = client.post("/v1/auth/login", json={
            "email": "login@example.com",
            "password": "mypassword",
        })
        assert res.status_code == 200
        assert res.json()["accessToken"]

    def test_returns_401_for_wrong_password(self, client):
        client.post("/v1/auth/register", json={
            "email": "login2@example.com",
            "password": "correctpassword",
            "firstName": "L",
            "lastName": "U",
            "role": "pet_owner",
        })
        res = client.post("/v1/auth/login", json={
            "email": "login2@example.com",
            "password": "wrongpassword",
        })
        assert res.status_code == 401
        assert res.json()["code"] == "INVALID_CREDENTIALS"

    def test_returns_401_for_non_existent_email(self, client):
        res = client.post("/v1/auth/login", json={
            "email": "nobody@example.com",
            "password": "password",
        })
        assert res.status_code == 401


class TestLogout:
    def test_returns_204_with_valid_token(self, client):
        reg = client.post("/v1/auth/register", json={
            "email": "logout@example.com",
            "password": "password123",
            "firstName": "L",
            "lastName": "O",
            "role": "pet_owner",
        })
        token = reg.json()["accessToken"]
        res = client.post("/v1/auth/logout", headers=auth_header(token))
        assert res.status_code == 204

    def test_returns_401_without_token(self, client):
        res = client.post("/v1/auth/logout")
        assert res.status_code == 401


class TestRefresh:
    def test_returns_new_tokens_with_valid_refresh_token(self, client):
        reg = client.post("/v1/auth/register", json={
            "email": "refresh@example.com",
            "password": "password123",
            "firstName": "R",
            "lastName": "F",
            "role": "pet_owner",
        })
        res = client.post("/v1/auth/refresh", json={"refreshToken": reg.json()["refreshToken"]})
        assert res.status_code == 200
        assert res.json()["accessToken"]
        assert res.json()["refreshToken"]

    def test_returns_401_with_invalid_refresh_token(self, client):
        res = client.post("/v1/auth/refresh", json={"refreshToken": "invalid-token"})
        assert res.status_code == 401
