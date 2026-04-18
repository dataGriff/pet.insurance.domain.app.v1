"""Pets routes — register, list, view, edit, remove."""
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Response

from src.middleware.authenticate import authenticate, require_role
from src.models import EditPetRequest, Pet, RegisterPetRequest
from src.store import store

router = APIRouter(prefix="/pets")


@router.get("", status_code=200, response_model=list[Pet])
async def list_pets(current_user: dict = Depends(require_role("pet_owner"))):
    """List all pets for the authenticated pet owner."""
    pets = [p for p in store["pets"].values() if p["petOwnerId"] == current_user["sub"]]
    return pets


@router.post("", status_code=201, response_model=Pet)
async def register_pet(
    body: RegisterPetRequest,
    current_user: dict = Depends(require_role("pet_owner")),
):
    """Register a new pet. Only pet_owner role may register pets."""
    now = datetime.now(tz=timezone.utc).isoformat()
    pet = {
        "id": str(uuid.uuid4()),
        "name": body.name,
        "species": body.species.value,
        "breed": body.breed,
        "dateOfBirth": body.dateOfBirth,
        "petOwnerId": current_user["sub"],
        "createdAt": now,
        "updatedAt": now,
    }
    store["pets"][pet["id"]] = pet
    return pet


@router.get("/{pet_id}", status_code=200, response_model=Pet)
async def get_pet(pet_id: str, current_user: dict = Depends(authenticate)):
    """View a single pet. Pet owners may only view their own pets. Agents may view any pet."""
    pet = store["pets"].get(pet_id)
    if not pet:
        raise HTTPException(
            status_code=404,
            detail={"code": "RESOURCE_NOT_FOUND", "message": "Pet not found."},
        )
    if current_user.get("role") == "pet_owner" and pet["petOwnerId"] != current_user["sub"]:
        raise HTTPException(
            status_code=403,
            detail={"code": "FORBIDDEN", "message": "You can only view your own pets."},
        )
    return pet


@router.patch("/{pet_id}", status_code=200, response_model=Pet)
async def edit_pet(
    pet_id: str,
    body: EditPetRequest,
    current_user: dict = Depends(require_role("pet_owner")),
):
    """Edit a pet. Only the pet owner who registered the pet may edit it."""
    pet = store["pets"].get(pet_id)
    if not pet:
        raise HTTPException(
            status_code=404,
            detail={"code": "RESOURCE_NOT_FOUND", "message": "Pet not found."},
        )
    if pet["petOwnerId"] != current_user["sub"]:
        raise HTTPException(
            status_code=403,
            detail={"code": "FORBIDDEN", "message": "You can only edit your own pets."},
        )

    if body.name is not None:
        pet["name"] = body.name
    if body.breed is not None:
        pet["breed"] = body.breed
    if body.dateOfBirth is not None:
        pet["dateOfBirth"] = body.dateOfBirth
    pet["updatedAt"] = datetime.now(tz=timezone.utc).isoformat()
    store["pets"][pet["id"]] = pet
    return pet


@router.delete("/{pet_id}", status_code=204)
async def remove_pet(
    pet_id: str,
    current_user: dict = Depends(require_role("pet_owner")),
):
    """Remove a registered pet. Only the pet owner who registered the pet may remove it."""
    pet = store["pets"].get(pet_id)
    if not pet:
        raise HTTPException(
            status_code=404,
            detail={"code": "RESOURCE_NOT_FOUND", "message": "Pet not found."},
        )
    if pet["petOwnerId"] != current_user["sub"]:
        raise HTTPException(
            status_code=403,
            detail={"code": "FORBIDDEN", "message": "You can only remove your own pets."},
        )
    del store["pets"][pet_id]
    return Response(status_code=204)
