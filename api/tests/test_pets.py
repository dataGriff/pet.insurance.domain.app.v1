"""Pets route tests."""
import pytest
from fastapi.testclient import TestClient

from src.main import app
from tests.helpers import auth_header, create_pet_owner_token, create_agent_token, seed_pet


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


class TestListPets:
    def test_returns_empty_list_when_no_pets_registered(self, client):
        owner = create_pet_owner_token()
        res = client.get("/v1/pets", headers=auth_header(owner["token"]))
        assert res.status_code == 200
        assert res.json() == []

    def test_returns_only_the_authenticated_owners_pets(self, client):
        owner = create_pet_owner_token()
        other = create_pet_owner_token()
        seed_pet(owner["user"]["id"])
        seed_pet(other["user"]["id"])
        res = client.get("/v1/pets", headers=auth_header(owner["token"]))
        assert res.status_code == 200
        assert len(res.json()) == 1
        assert res.json()[0]["petOwnerId"] == owner["user"]["id"]

    def test_agents_cannot_list_pets(self, client):
        agent = create_agent_token()
        res = client.get("/v1/pets", headers=auth_header(agent["token"]))
        assert res.status_code == 403

    def test_returns_401_without_token(self, client):
        res = client.get("/v1/pets")
        assert res.status_code == 401


class TestRegisterPet:
    def test_pet_owner_can_register_a_pet(self, client):
        owner = create_pet_owner_token()
        res = client.post(
            "/v1/pets",
            json={"name": "Buddy", "species": "dog", "breed": "Labrador", "dateOfBirth": "2020-03-15"},
            headers=auth_header(owner["token"]),
        )
        assert res.status_code == 201
        body = res.json()
        assert body["id"]
        assert body["name"] == "Buddy"
        assert body["species"] == "dog"
        assert body["breed"] == "Labrador"
        assert body["dateOfBirth"] == "2020-03-15"
        assert body["petOwnerId"] == owner["user"]["id"]
        assert body["createdAt"]
        assert body["updatedAt"]

    def test_registers_a_pet_with_no_breed(self, client):
        owner = create_pet_owner_token()
        res = client.post(
            "/v1/pets",
            json={"name": "Whiskers", "species": "cat", "dateOfBirth": "2019-06-10"},
            headers=auth_header(owner["token"]),
        )
        assert res.status_code == 201
        assert res.json()["breed"] is None

    def test_agents_cannot_register_pets(self, client):
        agent = create_agent_token()
        res = client.post(
            "/v1/pets",
            json={"name": "Buddy", "species": "dog", "dateOfBirth": "2020-03-15"},
            headers=auth_header(agent["token"]),
        )
        assert res.status_code == 403

    def test_returns_401_without_token(self, client):
        res = client.post("/v1/pets", json={"name": "Buddy", "species": "dog", "dateOfBirth": "2020-01-01"})
        assert res.status_code == 401


class TestGetPet:
    def test_pet_owner_can_view_their_own_pet(self, client):
        owner = create_pet_owner_token()
        pet = seed_pet(owner["user"]["id"])
        res = client.get(f"/v1/pets/{pet['id']}", headers=auth_header(owner["token"]))
        assert res.status_code == 200
        assert res.json()["id"] == pet["id"]
        assert res.json()["name"] == pet["name"]

    def test_agent_can_view_any_pet(self, client):
        owner = create_pet_owner_token()
        pet = seed_pet(owner["user"]["id"])
        agent = create_agent_token()
        res = client.get(f"/v1/pets/{pet['id']}", headers=auth_header(agent["token"]))
        assert res.status_code == 200
        assert res.json()["id"] == pet["id"]

    def test_pet_owner_cannot_view_another_owners_pet(self, client):
        owner = create_pet_owner_token()
        pet = seed_pet(owner["user"]["id"])
        other = create_pet_owner_token()
        res = client.get(f"/v1/pets/{pet['id']}", headers=auth_header(other["token"]))
        assert res.status_code == 403

    def test_returns_404_for_non_existent_pet(self, client):
        owner = create_pet_owner_token()
        res = client.get(
            "/v1/pets/00000000-0000-0000-0000-000000000000",
            headers=auth_header(owner["token"]),
        )
        assert res.status_code == 404
        assert res.json()["code"] == "RESOURCE_NOT_FOUND"

    def test_returns_401_without_token(self, client):
        res = client.get("/v1/pets/00000000-0000-0000-0000-000000000000")
        assert res.status_code == 401


class TestEditPet:
    def test_pet_owner_can_edit_their_own_pet(self, client):
        owner = create_pet_owner_token()
        pet = seed_pet(owner["user"]["id"])
        res = client.patch(
            f"/v1/pets/{pet['id']}",
            json={"name": "Max", "breed": "Golden Retriever"},
            headers=auth_header(owner["token"]),
        )
        assert res.status_code == 200
        assert res.json()["name"] == "Max"
        assert res.json()["breed"] == "Golden Retriever"

    def test_returns_403_when_editing_another_owners_pet(self, client):
        owner = create_pet_owner_token()
        pet = seed_pet(owner["user"]["id"])
        other = create_pet_owner_token()
        res = client.patch(
            f"/v1/pets/{pet['id']}",
            json={"name": "Stolen"},
            headers=auth_header(other["token"]),
        )
        assert res.status_code == 403

    def test_agents_cannot_edit_pets(self, client):
        owner = create_pet_owner_token()
        pet = seed_pet(owner["user"]["id"])
        agent = create_agent_token()
        res = client.patch(
            f"/v1/pets/{pet['id']}",
            json={"name": "Changed"},
            headers=auth_header(agent["token"]),
        )
        assert res.status_code == 403

    def test_returns_404_for_non_existent_pet(self, client):
        owner = create_pet_owner_token()
        res = client.patch(
            "/v1/pets/00000000-0000-0000-0000-000000000000",
            json={"name": "X"},
            headers=auth_header(owner["token"]),
        )
        assert res.status_code == 404


class TestRemovePet:
    def test_pet_owner_can_remove_their_own_pet(self, client):
        owner = create_pet_owner_token()
        pet = seed_pet(owner["user"]["id"])
        res = client.delete(f"/v1/pets/{pet['id']}", headers=auth_header(owner["token"]))
        assert res.status_code == 204

    def test_returns_403_when_removing_another_owners_pet(self, client):
        owner = create_pet_owner_token()
        pet = seed_pet(owner["user"]["id"])
        other = create_pet_owner_token()
        res = client.delete(f"/v1/pets/{pet['id']}", headers=auth_header(other["token"]))
        assert res.status_code == 403

    def test_agents_cannot_remove_pets(self, client):
        owner = create_pet_owner_token()
        pet = seed_pet(owner["user"]["id"])
        agent = create_agent_token()
        res = client.delete(f"/v1/pets/{pet['id']}", headers=auth_header(agent["token"]))
        assert res.status_code == 403

    def test_returns_404_for_non_existent_pet(self, client):
        owner = create_pet_owner_token()
        res = client.delete(
            "/v1/pets/00000000-0000-0000-0000-000000000000",
            headers=auth_header(owner["token"]),
        )
        assert res.status_code == 404
