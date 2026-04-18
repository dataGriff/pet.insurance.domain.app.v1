# Product Requirements Document — Pet Insurance

---

## Problem Statement

Pet owners need a simple, digital way to register their pets and submit insurance claims when their animals require veterinary treatment. Insurance agents need an efficient platform to review, approve, or reject those claims.

**Business:** Pet Insurance Domain v1 — digital claims management.

---

## Target Users / Personas

### Pet Owner

A person who has insured one or more pets and needs to manage claims.

- **Goal:** Register pets and submit claims quickly, then track their status.
- **Frustration:** Manual paper-based processes are slow, opaque, and require phone calls to check progress.

### Agent

An insurance agent responsible for reviewing and processing incoming claims.

- **Goal:** Review claim details alongside pet information, then approve or reject claims efficiently.
- **Frustration:** No centralised view of pending claims makes workload management difficult.

---

## Goals

1. Allow pet owners to register pets and submit insurance claims digitally.
2. Allow agents to review, approve, and reject claims.
3. Give both roles clear, real-time visibility into claim status.

---

## Non-Goals

1. Policy management — policies are not modelled in this v1.
2. Payment processing — claims are approved or rejected but no financial transactions occur.
3. Persistent storage — the in-memory store resets on restart.

---

## User Stories

### Authentication

#### US-001: Register as a pet owner or agent

**As a** new user,
**I want to** register with an email, password, and role,
**So that** I can access the platform.

**Acceptance Criteria:**
- [x] POST /v1/auth/register accepts `pet_owner` or `agent` role
- [x] Returns access token + refresh token on success
- [x] Returns 409 if email already registered

#### US-002: Log in and receive tokens

**As a** registered user,
**I want to** log in with my email and password,
**So that** I can get a fresh access token.

**Acceptance Criteria:**
- [x] POST /v1/auth/login returns 200 with tokens on valid credentials
- [x] Returns 401 on invalid credentials

---

### Pets

#### US-003: Register a pet

**As a** pet owner,
**I want to** register my pet with its name, species, breed, and date of birth,
**So that** I can associate insurance claims with it.

**Acceptance Criteria:**
- [x] POST /v1/pets registers a pet associated with the authenticated pet owner
- [x] Agents cannot register pets (403)

#### US-004: List my pets

**As a** pet owner,
**I want to** list all my registered pets,
**So that** I can see which pets I have insured.

**Acceptance Criteria:**
- [x] GET /v1/pets returns only the authenticated pet owner's pets
- [x] Agents cannot list pets (403)

#### US-005: View a pet

**As a** pet owner or agent,
**I want to** view a single pet's details,
**So that** I can see its full information.

**Acceptance Criteria:**
- [x] GET /v1/pets/{petId} returns the pet
- [x] Pet owners can only view their own pets (403 for another owner's pet)
- [x] Agents can view any pet
- [x] Returns 404 if not found

#### US-006: Edit a pet

**As a** pet owner,
**I want to** edit my pet's name, breed, or date of birth,
**So that** I can keep the information accurate.

**Acceptance Criteria:**
- [x] PATCH /v1/pets/{petId} edits the pet
- [x] Returns 403 if the pet belongs to a different pet owner
- [x] Agents cannot edit pets (403)

#### US-007: Remove a pet

**As a** pet owner,
**I want to** remove a pet I have registered,
**So that** it is no longer on my account.

**Acceptance Criteria:**
- [x] DELETE /v1/pets/{petId} removes the pet
- [x] Returns 403 if the pet belongs to a different pet owner
- [x] Agents cannot remove pets (403)

---

### Claims

#### US-008: Submit a claim

**As a** pet owner,
**I want to** submit an insurance claim for one of my pets,
**So that** I can seek reimbursement for veterinary costs.

**Acceptance Criteria:**
- [x] POST /v1/claims submits a claim with `status: pending`
- [x] Claim is associated with the authenticated pet owner's ID
- [x] Agents cannot submit claims (403)

#### US-009: List claims

**As a** pet owner,
**I want to** list all my claims,
**So that** I can track their status.

**As an** agent,
**I want to** list all claims across all pet owners,
**So that** I can manage my review workload.

**Acceptance Criteria:**
- [x] GET /v1/claims returns paginated list
- [x] Pet owners see only their own claims
- [x] Agents see all claims

#### US-010: View a claim

**As a** pet owner or agent,
**I want to** view the details of a single claim,
**So that** I can see the full information.

**Acceptance Criteria:**
- [x] GET /v1/claims/{claimId} returns the claim
- [x] Pet owners can only view their own claims (403 for another owner's claim)
- [x] Agents can view any claim
- [x] Returns 404 if not found

#### US-011: Approve a claim

**As an** agent,
**I want to** approve a pending claim,
**So that** the pet owner can receive reimbursement.

**Acceptance Criteria:**
- [x] POST /v1/claims/{claimId}/approve transitions claim to `approved`
- [x] Returns 409 if claim is not in `pending` status
- [x] Pet owners cannot approve claims (403)

#### US-012: Reject a claim

**As an** agent,
**I want to** reject a pending claim with a reason,
**So that** the pet owner understands why it was not approved.

**Acceptance Criteria:**
- [x] POST /v1/claims/{claimId}/reject transitions claim to `rejected`
- [x] Returns 409 if claim is not in `pending` status
- [x] Pet owners cannot reject claims (403)

#### US-013: Cancel a claim

**As a** pet owner,
**I want to** cancel a pending claim I submitted,
**So that** I can withdraw it if it was submitted in error.

**Acceptance Criteria:**
- [x] DELETE /v1/claims/{claimId} removes a pending claim
- [x] Returns 409 if claim is not in `pending` status
- [x] Returns 403 if the claim belongs to a different pet owner
- [x] Agents cannot cancel claims (403)

---

## Constraints

1. In-memory store only (no database).
2. Python (FastAPI/Uvicorn) only.

---

## Success Metrics

1. All tests pass — `task api:test`.
2. OpenAPI and AsyncAPI lint cleanly — `task lint`.
3. A new developer can understand the full domain in under 5 minutes.

