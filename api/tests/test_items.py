"""Items route tests."""
import pytest
from fastapi.testclient import TestClient

from src.main import app
from tests.helpers import create_contributor_token, create_viewer_token, seed_item


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


class TestListItems:
    def test_returns_empty_list_when_no_items_exist(self, client):
        contrib = create_contributor_token()
        res = client.get("/v1/items", headers={"Authorization": f"Bearer {contrib['token']}"})
        assert res.status_code == 200
        assert res.json()["data"] == []
        assert res.json()["pagination"]["total"] == 0

    def test_returns_list_of_items(self, client):
        contrib = create_contributor_token()
        seed_item(contrib["user"]["id"])
        seed_item(contrib["user"]["id"])
        res = client.get("/v1/items", headers={"Authorization": f"Bearer {contrib['token']}"})
        assert res.status_code == 200
        assert len(res.json()["data"]) == 2
        assert res.json()["pagination"]["total"] == 2

    def test_viewers_can_list_items(self, client):
        contrib = create_contributor_token()
        seed_item(contrib["user"]["id"])
        viewer = create_viewer_token()
        res = client.get("/v1/items", headers={"Authorization": f"Bearer {viewer['token']}"})
        assert res.status_code == 200
        assert len(res.json()["data"]) == 1

    def test_returns_401_without_token(self, client):
        res = client.get("/v1/items")
        assert res.status_code == 401


class TestAddItem:
    def test_adds_an_item_as_contributor(self, client):
        contrib = create_contributor_token()
        res = client.post(
            "/v1/items",
            json={"name": "My Item", "description": "A great item"},
            headers={"Authorization": f"Bearer {contrib['token']}"},
        )
        assert res.status_code == 201
        body = res.json()
        assert body["id"]
        assert body["name"] == "My Item"
        assert body["description"] == "A great item"
        assert body["status"] == "active"
        assert body["contributorId"]
        assert body["createdAt"]
        assert body["updatedAt"]

    def test_adds_an_item_with_null_description_when_omitted(self, client):
        contrib = create_contributor_token()
        res = client.post(
            "/v1/items",
            json={"name": "No Description Item"},
            headers={"Authorization": f"Bearer {contrib['token']}"},
        )
        assert res.status_code == 201
        assert res.json()["description"] is None

    def test_returns_403_when_viewer_tries_to_add(self, client):
        viewer = create_viewer_token()
        res = client.post(
            "/v1/items",
            json={"name": "Viewer Item"},
            headers={"Authorization": f"Bearer {viewer['token']}"},
        )
        assert res.status_code == 403

    def test_returns_401_without_token(self, client):
        res = client.post("/v1/items", json={"name": "Item"})
        assert res.status_code == 401


class TestGetItem:
    def test_returns_an_item_by_id(self, client):
        contrib = create_contributor_token()
        item = seed_item(contrib["user"]["id"])
        res = client.get(f"/v1/items/{item['id']}", headers={"Authorization": f"Bearer {contrib['token']}"})
        assert res.status_code == 200
        assert res.json()["id"] == item["id"]
        assert res.json()["name"] == item["name"]

    def test_viewers_can_get_an_item(self, client):
        contrib = create_contributor_token()
        item = seed_item(contrib["user"]["id"])
        viewer = create_viewer_token()
        res = client.get(f"/v1/items/{item['id']}", headers={"Authorization": f"Bearer {viewer['token']}"})
        assert res.status_code == 200
        assert res.json()["id"] == item["id"]

    def test_returns_404_for_non_existent_item(self, client):
        contrib = create_contributor_token()
        res = client.get(
            "/v1/items/00000000-0000-0000-0000-000000000000",
            headers={"Authorization": f"Bearer {contrib['token']}"},
        )
        assert res.status_code == 404
        assert res.json()["code"] == "RESOURCE_NOT_FOUND"

    def test_returns_401_without_token(self, client):
        res = client.get("/v1/items/00000000-0000-0000-0000-000000000000")
        assert res.status_code == 401


class TestEditItem:
    def test_contributor_can_edit_their_own_item(self, client):
        contrib = create_contributor_token()
        item = seed_item(contrib["user"]["id"])
        res = client.patch(
            f"/v1/items/{item['id']}",
            json={"name": "Updated Name", "status": "archived"},
            headers={"Authorization": f"Bearer {contrib['token']}"},
        )
        assert res.status_code == 200
        assert res.json()["name"] == "Updated Name"
        assert res.json()["status"] == "archived"

    def test_returns_403_when_editing_another_contributors_item(self, client):
        creator = create_contributor_token()
        item = seed_item(creator["user"]["id"])
        other = create_contributor_token()
        res = client.patch(
            f"/v1/items/{item['id']}",
            json={"name": "Stolen Update"},
            headers={"Authorization": f"Bearer {other['token']}"},
        )
        assert res.status_code == 403

    def test_returns_403_when_viewer_tries_to_edit(self, client):
        contrib = create_contributor_token()
        item = seed_item(contrib["user"]["id"])
        viewer = create_viewer_token()
        res = client.patch(
            f"/v1/items/{item['id']}",
            json={"name": "Viewer Update"},
            headers={"Authorization": f"Bearer {viewer['token']}"},
        )
        assert res.status_code == 403

    def test_returns_404_for_non_existent_item(self, client):
        contrib = create_contributor_token()
        res = client.patch(
            "/v1/items/00000000-0000-0000-0000-000000000000",
            json={"name": "X"},
            headers={"Authorization": f"Bearer {contrib['token']}"},
        )
        assert res.status_code == 404


class TestRemoveItem:
    def test_contributor_can_remove_their_own_item(self, client):
        contrib = create_contributor_token()
        item = seed_item(contrib["user"]["id"])
        res = client.delete(
            f"/v1/items/{item['id']}",
            headers={"Authorization": f"Bearer {contrib['token']}"},
        )
        assert res.status_code == 204

    def test_returns_403_when_removing_another_contributors_item(self, client):
        creator = create_contributor_token()
        item = seed_item(creator["user"]["id"])
        other = create_contributor_token()
        res = client.delete(
            f"/v1/items/{item['id']}",
            headers={"Authorization": f"Bearer {other['token']}"},
        )
        assert res.status_code == 403

    def test_returns_403_when_viewer_tries_to_remove(self, client):
        contrib = create_contributor_token()
        item = seed_item(contrib["user"]["id"])
        viewer = create_viewer_token()
        res = client.delete(
            f"/v1/items/{item['id']}",
            headers={"Authorization": f"Bearer {viewer['token']}"},
        )
        assert res.status_code == 403

    def test_returns_404_for_non_existent_item(self, client):
        contrib = create_contributor_token()
        res = client.delete(
            "/v1/items/00000000-0000-0000-0000-000000000000",
            headers={"Authorization": f"Bearer {contrib['token']}"},
        )
        assert res.status_code == 404
