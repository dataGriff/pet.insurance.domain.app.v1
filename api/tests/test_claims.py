"""Claims route tests."""
import pytest
from fastapi.testclient import TestClient

from src.main import app
from tests.helpers import auth_header, create_pet_owner_token, create_agent_token, seed_pet, seed_claim


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


class TestListClaims:
    def test_pet_owner_sees_only_their_own_claims(self, client):
        owner = create_pet_owner_token()
        other = create_pet_owner_token()
        pet = seed_pet(owner["user"]["id"])
        other_pet = seed_pet(other["user"]["id"])
        seed_claim(pet["id"], owner["user"]["id"])
        seed_claim(other_pet["id"], other["user"]["id"])
        res = client.get("/v1/claims", headers=auth_header(owner["token"]))
        assert res.status_code == 200
        data = res.json()["data"]
        assert len(data) == 1
        assert data[0]["petOwnerId"] == owner["user"]["id"]

    def test_agent_sees_all_claims(self, client):
        owner = create_pet_owner_token()
        other = create_pet_owner_token()
        pet1 = seed_pet(owner["user"]["id"])
        pet2 = seed_pet(other["user"]["id"])
        seed_claim(pet1["id"], owner["user"]["id"])
        seed_claim(pet2["id"], other["user"]["id"])
        agent = create_agent_token()
        res = client.get("/v1/claims", headers=auth_header(agent["token"]))
        assert res.status_code == 200
        assert res.json()["pagination"]["total"] == 2

    def test_returns_empty_list_when_no_claims_exist(self, client):
        owner = create_pet_owner_token()
        res = client.get("/v1/claims", headers=auth_header(owner["token"]))
        assert res.status_code == 200
        assert res.json()["data"] == []
        assert res.json()["pagination"]["total"] == 0

    def test_returns_401_without_token(self, client):
        res = client.get("/v1/claims")
        assert res.status_code == 401


class TestSubmitClaim:
    def test_pet_owner_can_submit_a_claim(self, client):
        owner = create_pet_owner_token()
        pet = seed_pet(owner["user"]["id"])
        res = client.post(
            "/v1/claims",
            json={"petId": pet["id"], "amount": 250.00, "description": "Routine check-up"},
            headers=auth_header(owner["token"]),
        )
        assert res.status_code == 201
        body = res.json()
        assert body["id"]
        assert body["petId"] == pet["id"]
        assert body["petOwnerId"] == owner["user"]["id"]
        assert body["amount"] == 250.00
        assert body["description"] == "Routine check-up"
        assert body["status"] == "pending"
        assert body["createdAt"]
        assert body["updatedAt"]

    def test_agents_cannot_submit_claims(self, client):
        agent = create_agent_token()
        owner = create_pet_owner_token()
        pet = seed_pet(owner["user"]["id"])
        res = client.post(
            "/v1/claims",
            json={"petId": pet["id"], "amount": 100.00, "description": "Treatment"},
            headers=auth_header(agent["token"]),
        )
        assert res.status_code == 403

    def test_returns_401_without_token(self, client):
        res = client.post("/v1/claims", json={"petId": "x", "amount": 100.0, "description": "x"})
        assert res.status_code == 401


class TestGetClaim:
    def test_pet_owner_can_view_their_own_claim(self, client):
        owner = create_pet_owner_token()
        pet = seed_pet(owner["user"]["id"])
        claim = seed_claim(pet["id"], owner["user"]["id"])
        res = client.get(f"/v1/claims/{claim['id']}", headers=auth_header(owner["token"]))
        assert res.status_code == 200
        assert res.json()["id"] == claim["id"]

    def test_agent_can_view_any_claim(self, client):
        owner = create_pet_owner_token()
        pet = seed_pet(owner["user"]["id"])
        claim = seed_claim(pet["id"], owner["user"]["id"])
        agent = create_agent_token()
        res = client.get(f"/v1/claims/{claim['id']}", headers=auth_header(agent["token"]))
        assert res.status_code == 200
        assert res.json()["id"] == claim["id"]

    def test_pet_owner_cannot_view_another_owners_claim(self, client):
        owner = create_pet_owner_token()
        pet = seed_pet(owner["user"]["id"])
        claim = seed_claim(pet["id"], owner["user"]["id"])
        other = create_pet_owner_token()
        res = client.get(f"/v1/claims/{claim['id']}", headers=auth_header(other["token"]))
        assert res.status_code == 403

    def test_returns_404_for_non_existent_claim(self, client):
        owner = create_pet_owner_token()
        res = client.get(
            "/v1/claims/00000000-0000-0000-0000-000000000000",
            headers=auth_header(owner["token"]),
        )
        assert res.status_code == 404
        assert res.json()["code"] == "RESOURCE_NOT_FOUND"

    def test_returns_401_without_token(self, client):
        res = client.get("/v1/claims/00000000-0000-0000-0000-000000000000")
        assert res.status_code == 401


class TestApproveClaim:
    def test_agent_can_approve_a_pending_claim(self, client):
        owner = create_pet_owner_token()
        pet = seed_pet(owner["user"]["id"])
        claim = seed_claim(pet["id"], owner["user"]["id"])
        agent = create_agent_token()
        res = client.post(
            f"/v1/claims/{claim['id']}/approve",
            headers=auth_header(agent["token"]),
        )
        assert res.status_code == 200
        assert res.json()["status"] == "approved"

    def test_pet_owners_cannot_approve_claims(self, client):
        owner = create_pet_owner_token()
        pet = seed_pet(owner["user"]["id"])
        claim = seed_claim(pet["id"], owner["user"]["id"])
        res = client.post(
            f"/v1/claims/{claim['id']}/approve",
            headers=auth_header(owner["token"]),
        )
        assert res.status_code == 403

    def test_returns_409_when_approving_a_non_pending_claim(self, client):
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

    def test_returns_404_for_non_existent_claim(self, client):
        agent = create_agent_token()
        res = client.post(
            "/v1/claims/00000000-0000-0000-0000-000000000000/approve",
            headers=auth_header(agent["token"]),
        )
        assert res.status_code == 404


class TestRejectClaim:
    def test_agent_can_reject_a_pending_claim(self, client):
        owner = create_pet_owner_token()
        pet = seed_pet(owner["user"]["id"])
        claim = seed_claim(pet["id"], owner["user"]["id"])
        agent = create_agent_token()
        res = client.post(
            f"/v1/claims/{claim['id']}/reject",
            headers=auth_header(agent["token"]),
        )
        assert res.status_code == 200
        assert res.json()["status"] == "rejected"

    def test_pet_owners_cannot_reject_claims(self, client):
        owner = create_pet_owner_token()
        pet = seed_pet(owner["user"]["id"])
        claim = seed_claim(pet["id"], owner["user"]["id"])
        res = client.post(
            f"/v1/claims/{claim['id']}/reject",
            headers=auth_header(owner["token"]),
        )
        assert res.status_code == 403

    def test_returns_409_when_rejecting_a_non_pending_claim(self, client):
        owner = create_pet_owner_token()
        pet = seed_pet(owner["user"]["id"])
        claim = seed_claim(pet["id"], owner["user"]["id"], status="rejected")
        agent = create_agent_token()
        res = client.post(
            f"/v1/claims/{claim['id']}/reject",
            headers=auth_header(agent["token"]),
        )
        assert res.status_code == 409
        assert res.json()["code"] == "INVALID_STATUS"

    def test_returns_404_for_non_existent_claim(self, client):
        agent = create_agent_token()
        res = client.post(
            "/v1/claims/00000000-0000-0000-0000-000000000000/reject",
            headers=auth_header(agent["token"]),
        )
        assert res.status_code == 404


class TestCancelClaim:
    def test_pet_owner_can_cancel_their_own_pending_claim(self, client):
        owner = create_pet_owner_token()
        pet = seed_pet(owner["user"]["id"])
        claim = seed_claim(pet["id"], owner["user"]["id"])
        res = client.delete(
            f"/v1/claims/{claim['id']}",
            headers=auth_header(owner["token"]),
        )
        assert res.status_code == 204

    def test_returns_403_when_cancelling_another_owners_claim(self, client):
        owner = create_pet_owner_token()
        pet = seed_pet(owner["user"]["id"])
        claim = seed_claim(pet["id"], owner["user"]["id"])
        other = create_pet_owner_token()
        res = client.delete(
            f"/v1/claims/{claim['id']}",
            headers=auth_header(other["token"]),
        )
        assert res.status_code == 403

    def test_agents_cannot_cancel_claims(self, client):
        owner = create_pet_owner_token()
        pet = seed_pet(owner["user"]["id"])
        claim = seed_claim(pet["id"], owner["user"]["id"])
        agent = create_agent_token()
        res = client.delete(
            f"/v1/claims/{claim['id']}",
            headers=auth_header(agent["token"]),
        )
        assert res.status_code == 403

    def test_returns_409_when_cancelling_an_approved_claim(self, client):
        owner = create_pet_owner_token()
        pet = seed_pet(owner["user"]["id"])
        claim = seed_claim(pet["id"], owner["user"]["id"], status="approved")
        res = client.delete(
            f"/v1/claims/{claim['id']}",
            headers=auth_header(owner["token"]),
        )
        assert res.status_code == 409
        assert res.json()["code"] == "INVALID_STATUS"

    def test_returns_404_for_non_existent_claim(self, client):
        owner = create_pet_owner_token()
        res = client.delete(
            "/v1/claims/00000000-0000-0000-0000-000000000000",
            headers=auth_header(owner["token"]),
        )
        assert res.status_code == 404
