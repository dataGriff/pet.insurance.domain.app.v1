"""Contract tests — validate response shapes match the OpenAPI spec."""
import pytest
from fastapi.testclient import TestClient

from src.main import app
from tests.helpers import create_contributor_token, create_viewer_token, seed_item


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


class TestAuthEndpoints:
    def test_register_returns_201_with_auth_response_shape(self, client):
        res = client.post("/v1/auth/register", json={
            "email": "test@example.com",
            "password": "password123",
            "firstName": "Test",
            "lastName": "User",
            "role": "contributor",
        })
        assert res.status_code == 201
        body = res.json()
        assert "accessToken" in body
        assert "refreshToken" in body
        assert "expiresIn" in body
        assert "id" in body["user"]
        assert "email" in body["user"]
        assert "firstName" in body["user"]
        assert "lastName" in body["user"]
        assert "role" in body["user"]

    def test_login_returns_200_with_auth_response_shape(self, client):
        client.post("/v1/auth/register", json={
            "email": "test2@example.com",
            "password": "password123",
            "firstName": "T",
            "lastName": "U",
            "role": "viewer",
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

    def test_logout_returns_204(self, client):
        contrib = create_contributor_token()
        res = client.post(
            "/v1/auth/logout",
            headers={"Authorization": f"Bearer {contrib['token']}"},
        )
        assert res.status_code == 204

    def test_refresh_returns_200_with_auth_response_shape(self, client):
        reg = client.post("/v1/auth/register", json={
            "email": "refresh@example.com",
            "password": "password123",
            "firstName": "R",
            "lastName": "T",
            "role": "contributor",
        })
        res = client.post("/v1/auth/refresh", json={"refreshToken": reg.json()["refreshToken"]})
        assert res.status_code == 200
        body = res.json()
        assert "accessToken" in body
        assert "refreshToken" in body


class TestItemEndpoints:
    def test_list_items_returns_200_with_item_list_shape(self, client):
        contrib = create_contributor_token()
        res = client.get("/v1/items", headers={"Authorization": f"Bearer {contrib['token']}"})
        assert res.status_code == 200
        body = res.json()
        assert "data" in body
        assert "pagination" in body
        assert "page" in body["pagination"]
        assert "pageSize" in body["pagination"]
        assert "total" in body["pagination"]

    def test_add_item_returns_201_with_item_shape(self, client):
        contrib = create_contributor_token()
        res = client.post(
            "/v1/items",
            json={"name": "Shape Test Item"},
            headers={"Authorization": f"Bearer {contrib['token']}"},
        )
        assert res.status_code == 201
        body = res.json()
        assert "id" in body
        assert body["name"] == "Shape Test Item"
        assert body["description"] is None
        assert body["status"] == "active"
        assert "contributorId" in body
        assert "createdAt" in body
        assert "updatedAt" in body

    def test_get_item_returns_200_with_item_shape(self, client):
        contrib = create_contributor_token()
        item = seed_item(contrib["user"]["id"])
        res = client.get(
            f"/v1/items/{item['id']}",
            headers={"Authorization": f"Bearer {contrib['token']}"},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["id"] == item["id"]
        assert "name" in body
        assert "status" in body
        assert "contributorId" in body

    def test_edit_item_returns_200_with_edited_item_shape(self, client):
        contrib = create_contributor_token()
        item = seed_item(contrib["user"]["id"])
        res = client.patch(
            f"/v1/items/{item['id']}",
            json={"name": "Patched Item", "status": "archived"},
            headers={"Authorization": f"Bearer {contrib['token']}"},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["name"] == "Patched Item"
        assert body["status"] == "archived"
        assert "updatedAt" in body

    def test_remove_item_returns_204(self, client):
        contrib = create_contributor_token()
        item = seed_item(contrib["user"]["id"])
        res = client.delete(
            f"/v1/items/{item['id']}",
            headers={"Authorization": f"Bearer {contrib['token']}"},
        )
        assert res.status_code == 204


class TestErrorResponses:
    def test_returns_401_when_no_token_provided(self, client):
        res = client.get("/v1/items")
        assert res.status_code == 401
        body = res.json()
        assert "code" in body
        assert "message" in body

    def test_returns_403_when_viewer_accesses_contributor_only_endpoint(self, client):
        viewer = create_viewer_token()
        res = client.post(
            "/v1/items",
            json={"name": "Forbidden Item"},
            headers={"Authorization": f"Bearer {viewer['token']}"},
        )
        assert res.status_code == 403
        assert "code" in res.json()

    def test_returns_404_for_non_existent_resource(self, client):
        contrib = create_contributor_token()
        res = client.get(
            "/v1/items/00000000-0000-0000-0000-000000000000",
            headers={"Authorization": f"Bearer {contrib['token']}"},
        )
        assert res.status_code == 404
        assert res.json()["code"] == "RESOURCE_NOT_FOUND"

    def test_returns_409_for_duplicate_email_on_register(self, client):
        payload = {
            "email": "dup@example.com",
            "password": "password123",
            "firstName": "D",
            "lastName": "U",
            "role": "contributor",
        }
        client.post("/v1/auth/register", json=payload)
        res = client.post("/v1/auth/register", json=payload)
        assert res.status_code == 409
        assert res.json()["code"] == "DUPLICATE_EMAIL"
