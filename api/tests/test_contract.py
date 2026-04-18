"""Contract tests — validate response shapes match the OpenAPI spec."""
import pytest
from fastapi.testclient import TestClient

from src.main import app
from tests.helpers import auth_header, create_pet_owner_token, create_agent_token, seed_pet, seed_claim


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


class TestAuthShapes:
    def test_register_returns_201_with_auth_response_shape(self, client):
        res = client.post("/v1/auth/register", json={
            "email": "test@example.com",
            "password": "password123",
            "firstName": "Test",
            "lastName": "User",
            "role": "pet_owner",
        })
        assert res.status_code == 201
        body = res.json()
        assert "accessToken" in body
        assert "refreshToken" in body
        assert "expiresIn" in body
        user = body["user"]
        assert "id" in user
        assert "email" in user
        assert "firstName" in user
        assert "lastName" in user
        assert user["role"] == "pet_owner"

    def test_login_returns_200_with_auth_response_shape(self, client):
        client.post("/v1/auth/register", json={
            "email": "test2@example.com",
            "password": "password123",
            "firstName": "T",
            "lastName": "U",
            "role": "agent",
        })
        res = client.post("/v1/auth/login", json={
            "email": "test2@example.com",
            "password": "password123",
        })
        assert res.status_code == 200
        body = res.json()
        assert "accessToken" in body
        assert "refreshToken" in body
        assert "expiresIn" in body
        assert "id" in body["user"]


class TestPetShapes:
    def test_register_pet_returns_201_with_pet_shape(self, client):
        owner = create_pet_owner_token()
        res = client.post(
            "/v1/pets",
            json={"name": "Buddy", "species": "dog", "dateOfBirth": "2020-03-15"},
            headers=auth_header(owner["token"]),
        )
        assert res.status_code == 201
        body = res.json()
        assert "id" in body
        assert body["name"] == "Buddy"
        assert body["species"] == "dog"
        assert body["breed"] is None
        assert body["dateOfBirth"] == "2020-03-15"
        assert "petOwnerId" in body
        assert "createdAt" in body
        assert "updatedAt" in body

    def test_list_pets_returns_200_with_array_of_pet_shape(self, client):
        owner = create_pet_owner_token()
        seed_pet(owner["user"]["id"])
        res = client.get("/v1/pets", headers=auth_header(owner["token"]))
        assert res.status_code == 200
        assert isinstance(res.json(), list)
        body = res.json()[0]
        assert "id" in body
        assert "name" in body
        assert "species" in body
        assert "petOwnerId" in body

    def test_get_pet_returns_200_with_pet_shape(self, client):
        owner = create_pet_owner_token()
        pet = seed_pet(owner["user"]["id"])
        res = client.get(f"/v1/pets/{pet['id']}", headers=auth_header(owner["token"]))
        assert res.status_code == 200
        body = res.json()
        assert body["id"] == pet["id"]
        assert "species" in body
        assert "petOwnerId" in body


class TestClaimShapes:
    def test_submit_claim_returns_201_with_claim_shape(self, client):
        owner = create_pet_owner_token()
        pet = seed_pet(owner["user"]["id"])
        res = client.post(
            "/v1/claims",
            json={"petId": pet["id"], "amount": 150.00, "description": "Dental treatment"},
            headers=auth_header(owner["token"]),
        )
        assert res.status_code == 201
        body = res.json()
        assert "id" in body
        assert body["petId"] == pet["id"]
        assert body["amount"] == 150.00
        assert body["status"] == "pending"
        assert "petOwnerId" in body
        assert "createdAt" in body
        assert "updatedAt" in body

    def test_list_claims_returns_200_with_claim_list_shape(self, client):
        owner = create_pet_owner_token()
        res = client.get("/v1/claims", headers=auth_header(owner["token"]))
        assert res.status_code == 200
        body = res.json()
        assert "data" in body
        assert "pagination" in body
        pagination = body["pagination"]
        assert "page" in pagination
        assert "pageSize" in pagination
        assert "total" in pagination

    def test_approve_claim_returns_200_with_updated_claim_shape(self, client):
        owner = create_pet_owner_token()
        pet = seed_pet(owner["user"]["id"])
        claim = seed_claim(pet["id"], owner["user"]["id"])
        agent = create_agent_token()
        res = client.post(
            f"/v1/claims/{claim['id']}/approve",
            headers=auth_header(agent["token"]),
        )
        assert res.status_code == 200
        body = res.json()
        assert body["status"] == "approved"
        assert "updatedAt" in body

    def test_reject_claim_returns_200_with_updated_claim_shape(self, client):
        owner = create_pet_owner_token()
        pet = seed_pet(owner["user"]["id"])
        claim = seed_claim(pet["id"], owner["user"]["id"])
        agent = create_agent_token()
        res = client.post(
            f"/v1/claims/{claim['id']}/reject",
            headers=auth_header(agent["token"]),
        )
        assert res.status_code == 200
        body = res.json()
        assert body["status"] == "rejected"


class TestErrorShapes:
    def test_returns_401_when_no_token_provided(self, client):
        res = client.get("/v1/claims")
        assert res.status_code == 401
        body = res.json()
        assert "code" in body
        assert "message" in body

    def test_returns_403_when_agent_tries_to_register_pet(self, client):
        agent = create_agent_token()
        res = client.post(
            "/v1/pets",
            json={"name": "Buddy", "species": "dog", "dateOfBirth": "2020-01-01"},
            headers=auth_header(agent["token"]),
        )
        assert res.status_code == 403
        body = res.json()
        assert "code" in body

    def test_returns_404_for_non_existent_pet(self, client):
        owner = create_pet_owner_token()
        res = client.get(
            "/v1/pets/00000000-0000-0000-0000-000000000000",
            headers=auth_header(owner["token"]),
        )
        assert res.status_code == 404
        assert res.json()["code"] == "RESOURCE_NOT_FOUND"

    def test_returns_409_for_invalid_status_transition(self, client):
        owner = create_pet_owner_token()
        pet = seed_pet(owner["user"]["id"])
        claim = seed_claim(pet["id"], owner["user"]["id"], status="approved")
        agent = create_agent_token()
        res = client.post(
            f"/v1/claims/{claim['id']}/approve",
            headers=auth_header(agent["token"]),
        )
        assert res.status_code == 409
        assert res.json()["code"] == "INVALID_STATUS"
