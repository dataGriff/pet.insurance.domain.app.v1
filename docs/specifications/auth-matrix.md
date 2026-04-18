# Auth Matrix — Pet Insurance

---

## Roles

| Role | Description |
|------|-------------|
| `pet_owner` | Can register pets and submit/cancel own claims |
| `agent` | Can view pets and review (approve/reject) claims |

## Authentication

All protected routes require a `Bearer` JWT token in the `Authorization` header.
Unauthenticated requests to protected routes return `401 Unauthorized`.

Tokens are issued via `POST /v1/auth/login` and refreshed via `POST /v1/auth/refresh`.

## Auth Matrix

### Authentication

| Operation | Endpoint | Public | pet_owner | agent |
|-----------|----------|--------|-----------|-------|
| Register | `POST /v1/auth/register` | 🌐 | 🌐 | 🌐 |
| Login | `POST /v1/auth/login` | 🌐 | 🌐 | 🌐 |
| Refresh token | `POST /v1/auth/refresh` | 🌐 | 🌐 | 🌐 |
| Logout | `POST /v1/auth/logout` | ❌ | ✅ | ✅ |

### Pets

| Operation | Endpoint | Public | pet_owner | agent |
|-----------|----------|--------|-----------|-------|
| List pets | `GET /v1/pets` | ❌ | ✅ own | ❌ |
| Register pet | `POST /v1/pets` | ❌ | ✅ | ❌ |
| View pet | `GET /v1/pets/{petId}` | ❌ | ✅ own | ✅ |
| Edit pet | `PATCH /v1/pets/{petId}` | ❌ | ✅ own | ❌ |
| Remove pet | `DELETE /v1/pets/{petId}` | ❌ | ✅ own | ❌ |

### Claims

| Operation | Endpoint | Public | pet_owner | agent |
|-----------|----------|--------|-----------|-------|
| List claims | `GET /v1/claims` | ❌ | ✅ own | ✅ all |
| Submit claim | `POST /v1/claims` | ❌ | ✅ | ❌ |
| View claim | `GET /v1/claims/{claimId}` | ❌ | ✅ own | ✅ |
| Approve claim | `POST /v1/claims/{claimId}/approve` | ❌ | ❌ | ✅ |
| Reject claim | `POST /v1/claims/{claimId}/reject` | ❌ | ❌ | ✅ |
| Cancel claim | `DELETE /v1/claims/{claimId}` | ❌ | ✅ own | ❌ |

Legend:
- 🌐 Public (no auth required)
- ✅ Allowed
- ✅ own — Allowed only for the pet owner's own records
- ✅ all — Allowed for all records regardless of owner
- ❌ Forbidden

## Ownership Rules

- **Pet**: A `pet_owner` may only list, view, edit, or remove pets where `pet.petOwnerId` matches their user ID.
- **Claim**: A `pet_owner` may only view or cancel claims where `claim.petOwnerId` matches their user ID. Attempting to access another owner's records returns `403 Forbidden`.

## Status Rules

- Approve and reject actions are only permitted when `claim.status === "pending"`. Attempting to act on a non-pending claim returns `409 Conflict`.
- Cancel (DELETE) is only permitted when `claim.status === "pending"`. Attempting to cancel a non-pending claim returns `409 Conflict`.

## Error Responses

| Scenario | HTTP Status | Error Code |
|----------|-------------|------------|
| No token provided | `401` | `AUTHENTICATION_REQUIRED` |
| Token expired | `401` | `TOKEN_EXPIRED` |
| Valid token, wrong role | `403` | `FORBIDDEN` |
| Valid token, not resource owner | `403` | `FORBIDDEN` |
| Claim not in pending status | `409` | `INVALID_STATUS` |
