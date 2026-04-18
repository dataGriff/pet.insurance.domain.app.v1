"""Items routes — list, add, view, edit, remove."""
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from src.middleware.authenticate import authenticate, require_role
from src.models import CreateItemRequest, Item, ItemList, Pagination, UpdateItemRequest
from src.store import store

router = APIRouter(prefix="/items")


@router.get("", status_code=200, response_model=ItemList)
async def list_items(
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=20, ge=1, le=100),
    current_user: dict = Depends(authenticate),
):
    """List all items with pagination. Accessible by both contributor and viewer roles."""
    all_items = list(store["items"].values())
    total = len(all_items)
    start = (page - 1) * pageSize
    data = all_items[start: start + pageSize]
    return {"data": data, "pagination": {"page": page, "pageSize": pageSize, "total": total}}


@router.post("", status_code=201, response_model=Item)
async def add_item(
    body: CreateItemRequest,
    current_user: dict = Depends(require_role("contributor")),
):
    """Add a new item to the catalogue. Only contributor role may add items."""
    now = datetime.now(tz=timezone.utc).isoformat()
    item = {
        "id": str(uuid.uuid4()),
        "name": body.name,
        "description": body.description,
        "status": "active",
        "contributorId": current_user["sub"],
        "createdAt": now,
        "updatedAt": now,
    }
    store["items"][item["id"]] = item
    return item


@router.get("/{item_id}", status_code=200, response_model=Item)
async def get_item(item_id: str, current_user: dict = Depends(authenticate)):
    """View a single item by ID. Accessible by both contributor and viewer roles."""
    item = store["items"].get(item_id)
    if not item:
        raise HTTPException(
            status_code=404,
            detail={"code": "RESOURCE_NOT_FOUND", "message": "Item not found."},
        )
    return item


@router.patch("/{item_id}", status_code=200, response_model=Item)
async def edit_item(
    item_id: str,
    body: UpdateItemRequest,
    current_user: dict = Depends(require_role("contributor")),
):
    """Edit an item. Only the contributor who added the item may edit it."""
    item = store["items"].get(item_id)
    if not item:
        raise HTTPException(
            status_code=404,
            detail={"code": "RESOURCE_NOT_FOUND", "message": "Item not found."},
        )
    if item["contributorId"] != current_user["sub"]:
        raise HTTPException(
            status_code=403,
            detail={"code": "FORBIDDEN", "message": "You can only edit your own items."},
        )

    if body.name is not None:
        item["name"] = body.name
    if body.description is not None:
        item["description"] = body.description
    if body.status is not None:
        item["status"] = body.status
    item["updatedAt"] = datetime.now(tz=timezone.utc).isoformat()
    store["items"][item["id"]] = item
    return item


@router.delete("/{item_id}", status_code=204)
async def remove_item(
    item_id: str,
    current_user: dict = Depends(require_role("contributor")),
):
    """Remove an item from the catalogue. Only the contributor who added the item may remove it."""
    item = store["items"].get(item_id)
    if not item:
        raise HTTPException(
            status_code=404,
            detail={"code": "RESOURCE_NOT_FOUND", "message": "Item not found."},
        )
    if item["contributorId"] != current_user["sub"]:
        raise HTTPException(
            status_code=403,
            detail={"code": "FORBIDDEN", "message": "You can only remove your own items."},
        )
    del store["items"][item_id]
    return Response(status_code=204)
