"""Claims routes — submit, list, view, approve, reject, cancel."""
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Response

from src.middleware.authenticate import authenticate, require_role
from src.models import Claim, ClaimList, Pagination, SubmitClaimRequest
from src.store import store

router = APIRouter(prefix="/claims")


@router.get("", status_code=200, response_model=ClaimList)
async def list_claims(
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=20, ge=1, le=100),
    current_user: dict = Depends(authenticate),
):
    """List claims. Pet owners see only their own claims; agents see all claims."""
    role = current_user.get("role")
    if role == "pet_owner":
        all_claims = [c for c in store["claims"].values() if c["petOwnerId"] == current_user["sub"]]
    else:
        all_claims = list(store["claims"].values())

    total = len(all_claims)
    start = (page - 1) * pageSize
    data = all_claims[start: start + pageSize]
    return {"data": data, "pagination": {"page": page, "pageSize": pageSize, "total": total}}


@router.post("", status_code=201, response_model=Claim)
async def submit_claim(
    body: SubmitClaimRequest,
    current_user: dict = Depends(require_role("pet_owner")),
):
    """Submit a new insurance claim. Only pet_owner role may submit claims."""
    now = datetime.now(tz=timezone.utc).isoformat()
    claim = {
        "id": str(uuid.uuid4()),
        "petId": body.petId,
        "petOwnerId": current_user["sub"],
        "amount": body.amount,
        "description": body.description,
        "status": "pending",
        "createdAt": now,
        "updatedAt": now,
    }
    store["claims"][claim["id"]] = claim
    return claim


@router.get("/{claim_id}", status_code=200, response_model=Claim)
async def get_claim(claim_id: str, current_user: dict = Depends(authenticate)):
    """View a single claim. Pet owners may only view their own claims. Agents may view any claim."""
    claim = store["claims"].get(claim_id)
    if not claim:
        raise HTTPException(
            status_code=404,
            detail={"code": "RESOURCE_NOT_FOUND", "message": "Claim not found."},
        )
    if current_user.get("role") == "pet_owner" and claim["petOwnerId"] != current_user["sub"]:
        raise HTTPException(
            status_code=403,
            detail={"code": "FORBIDDEN", "message": "You can only view your own claims."},
        )
    return claim


@router.post("/{claim_id}/approve", status_code=200, response_model=Claim)
async def approve_claim(
    claim_id: str,
    current_user: dict = Depends(require_role("agent")),
):
    """Approve a pending claim. Only agent role may approve claims."""
    claim = store["claims"].get(claim_id)
    if not claim:
        raise HTTPException(
            status_code=404,
            detail={"code": "RESOURCE_NOT_FOUND", "message": "Claim not found."},
        )
    if claim["status"] != "pending":
        raise HTTPException(
            status_code=409,
            detail={"code": "INVALID_STATUS", "message": "Only pending claims can be approved."},
        )
    claim["status"] = "approved"
    claim["updatedAt"] = datetime.now(tz=timezone.utc).isoformat()
    store["claims"][claim_id] = claim
    return claim


@router.post("/{claim_id}/reject", status_code=200, response_model=Claim)
async def reject_claim(
    claim_id: str,
    current_user: dict = Depends(require_role("agent")),
):
    """Reject a pending claim. Only agent role may reject claims."""
    claim = store["claims"].get(claim_id)
    if not claim:
        raise HTTPException(
            status_code=404,
            detail={"code": "RESOURCE_NOT_FOUND", "message": "Claim not found."},
        )
    if claim["status"] != "pending":
        raise HTTPException(
            status_code=409,
            detail={"code": "INVALID_STATUS", "message": "Only pending claims can be rejected."},
        )
    claim["status"] = "rejected"
    claim["updatedAt"] = datetime.now(tz=timezone.utc).isoformat()
    store["claims"][claim_id] = claim
    return claim


@router.delete("/{claim_id}", status_code=204)
async def cancel_claim(
    claim_id: str,
    current_user: dict = Depends(require_role("pet_owner")),
):
    """Cancel a pending claim. Only the pet owner who submitted the claim may cancel it."""
    claim = store["claims"].get(claim_id)
    if not claim:
        raise HTTPException(
            status_code=404,
            detail={"code": "RESOURCE_NOT_FOUND", "message": "Claim not found."},
        )
    if claim["petOwnerId"] != current_user["sub"]:
        raise HTTPException(
            status_code=403,
            detail={"code": "FORBIDDEN", "message": "You can only cancel your own claims."},
        )
    if claim["status"] != "pending":
        raise HTTPException(
            status_code=409,
            detail={"code": "INVALID_STATUS", "message": "Only pending claims can be cancelled."},
        )
    del store["claims"][claim_id]
    return Response(status_code=204)
