# Domain Model — Pet Insurance

---

## Overview

The **Pet Insurance** domain allows pet owners to register their pets and submit insurance claims for veterinary costs. Agents review and process those claims. There are two roles: `pet_owner` (registers pets and submits claims) and `agent` (reviews and approves or rejects claims).

---

## Entities

### User

Represents an authenticated user of the system.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | UUID | Yes | Unique identifier |
| `email` | string (email) | Yes | User's email address (unique) |
| `password` | string (hashed) | Yes | Bcrypt-hashed password (never returned in responses) |
| `firstName` | string | Yes | Given name |
| `lastName` | string | Yes | Family name |
| `role` | enum | Yes | `pet_owner` or `agent` |
| `createdAt` | ISO 8601 | Yes | Registration timestamp |

**Business Rules:**
- Email must be unique across all users.
- Password is stored as a bcrypt hash; never returned in API responses.
- Role is set at registration and cannot be changed via the API.

---

### Pet

Represents a pet registered by a pet owner.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | UUID | Yes | Unique identifier |
| `name` | string | Yes | Pet's name (min 1 char) |
| `species` | enum | Yes | `dog`, `cat`, `rabbit`, `bird`, or `other` |
| `breed` | string \| null | No | Breed or type (optional) |
| `dateOfBirth` | date (YYYY-MM-DD) | Yes | Pet's date of birth |
| `petOwnerId` | UUID | Yes | ID of the user who registered this pet |
| `createdAt` | ISO 8601 | Yes | Registration timestamp |
| `updatedAt` | ISO 8601 | Yes | Last update timestamp |

**Business Rules:**
- Only the pet owner who registered a pet may edit or remove it.
- Agents may view any pet but cannot register, edit, or remove pets.

---

### Claim

Represents an insurance claim submitted by a pet owner for a registered pet.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | UUID | Yes | Unique identifier |
| `petId` | UUID | Yes | ID of the pet this claim is for |
| `petOwnerId` | UUID | Yes | ID of the pet owner who submitted the claim |
| `amount` | number | Yes | Claimed amount in GBP (positive, max 2 decimal places) |
| `description` | string | Yes | Description of the veterinary treatment |
| `status` | enum | Yes | `pending`, `approved`, or `rejected` |
| `createdAt` | ISO 8601 | Yes | Submission timestamp |
| `updatedAt` | ISO 8601 | Yes | Last update timestamp |

**Business Rules:**
- `status` defaults to `pending` on submission.
- Only an agent may approve or reject a claim.
- Only the pet owner who submitted a claim may cancel it.
- A claim may only be approved or rejected when `status` is `pending`.
- A claim may only be cancelled when `status` is `pending`.

---

## Relationships

```
User (role=pet_owner) ──── registers many ──── Pet
User (role=pet_owner) ──── submits many ──────── Claim
Pet ──────────────────────── belongs to ──────── User (petOwnerId)
Claim ────────────────────── belongs to ──────── User (petOwnerId)
Claim ────────────────────── references ─────── Pet (petId)
```

---

## Aggregates

| Aggregate Root | Entities Contained | Description |
|---------------|-------------------|-------------|
| `Pet` | Pet | Self-contained; ownership tracked via `petOwnerId` |
| `Claim` | Claim | Self-contained; references Pet by `petId`, owner by `petOwnerId` |
| `User` | User | Self-contained; no nested child entities |

---

## Domain Events

| Event | Trigger | Channel |
|-------|---------|---------|
| `PetRegistered` | POST /v1/pets → 201 | `pet-insurance.pet.registered` |
| `ClaimSubmitted` | POST /v1/claims → 201 | `pet-insurance.claim.submitted` |
| `ClaimApproved` | POST /v1/claims/{claimId}/approve → 200 | `pet-insurance.claim.approved` |
| `ClaimRejected` | POST /v1/claims/{claimId}/reject → 200 | `pet-insurance.claim.rejected` |
| `ClaimCancelled` | DELETE /v1/claims/{claimId} → 204 | `pet-insurance.claim.cancelled` |

---

## Status Lifecycles

### Claim Status

```
pending ──► approved
pending ──► rejected
pending ──► [cancelled / removed]
```

| From | To | Trigger |
|------|----|---------|
| `pending` | `approved` | POST /v1/claims/{claimId}/approve (agent) |
| `pending` | `rejected` | POST /v1/claims/{claimId}/reject (agent) |
| `pending` | *(removed)* | DELETE /v1/claims/{claimId} (pet owner) |

Approved and rejected are terminal states — no further status transitions are permitted.

