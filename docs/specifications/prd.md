# Product Requirements Document — Items

> **Example domain.** This is the working reference implementation included with the Domain API Template.
> It is intentionally simple. Replace the contents of `docs/specifications/` with your own domain
> by running `task domain:init` and editing the generated files.

---

## Problem Statement

Teams building new APIs need a consistent, spec-driven starting point that demonstrates all the key patterns (auth, role-based access control, item lifecycle management, pagination, events) without domain complexity getting in the way.

**Business:** Domain API Template — reusable scaffold.

The **Items** domain provides a minimal, working example that anyone can understand in minutes.

## Target Users / Personas

### Contributor

A user who can add and manage their own items.

- **Goal:** Add items to the catalogue and keep them up to date.
- **Frustration:** Too many steps to add a simple item; can't easily archive old items.

### Viewer

A user who can browse the item catalogue but cannot make changes.

- **Goal:** Find and view items without clutter.
- **Frustration:** Accidental edits by other users affecting their view.

## Goals

1. Provide a minimal, running API example that demonstrates authentication, role-based access control, item lifecycle management, and pagination.
2. Keep the example simple enough that any developer can grasp the full domain in under 5 minutes.
3. Show — not just describe — the template patterns so they are easy to replicate in a new domain.

## Non-Goals

1. A real product use case (items has no real business meaning).
2. Complex state machines, nested resources, or domain events beyond simple lifecycle events.
3. Persistent storage — the in-memory store resets on restart.

## User Stories

### Authentication

#### US-001: Register as a contributor or viewer

**As a** new user,
**I want to** register with an email, password, and role,
**So that** I can access the API.

**Acceptance Criteria:**
- [x] POST /v1/auth/register accepts `contributor` or `viewer` role
- [x] Returns access token + refresh token on success
- [x] Returns 409 if email already registered

#### US-002: Log in and receive tokens

**As a** registered user,
**I want to** log in with my email and password,
**So that** I can get a fresh access token.

**Acceptance Criteria:**
- [x] POST /v1/auth/login returns 200 with tokens on valid credentials
- [x] Returns 401 on invalid credentials

### Items

#### US-003: Add an item to the catalogue

**As a** contributor,
**I want to** add a new item with a name and optional description,
**So that** it appears in the catalogue.

**Acceptance Criteria:**
- [x] POST /v1/items adds an item with `status: active`
- [x] Item is associated with the authenticated contributor's ID
- [x] Viewers cannot add items (403)

#### US-004: List all items

**As a** contributor or viewer,
**I want to** list all items with pagination,
**So that** I can browse the catalogue.

**Acceptance Criteria:**
- [x] GET /v1/items returns paginated list
- [x] Both roles can list items

#### US-005: View a single item

**As a** contributor or viewer,
**I want to** view the details of a single item,
**So that** I can see its full information.

**Acceptance Criteria:**
- [x] GET /v1/items/:itemId returns the item
- [x] Returns 404 if not found

#### US-006: Edit my own item

**As a** contributor,
**I want to** edit the name, description, or status of an item I added,
**So that** I can keep the catalogue accurate.

**Acceptance Criteria:**
- [x] PATCH /v1/items/:itemId edits the item
- [x] Returns 403 if the item belongs to a different contributor
- [x] Viewers cannot edit items (403)

#### US-007: Remove my own item from the catalogue

**As a** contributor,
**I want to** remove an item I added,
**So that** it is no longer in the catalogue.

**Acceptance Criteria:**
- [x] DELETE /v1/items/:itemId removes the item
- [x] Returns 403 if the item belongs to a different contributor
- [x] Viewers cannot remove items (403)

## Constraints

1. In-memory store only (no database).
2. No real business domain — items are intentionally generic.
3. JavaScript (Node.js/Express) only.

## Success Metrics

1. All tests pass — `task api:test`.
2. OpenAPI and AsyncAPI lint cleanly — `task lint`.
3. A new developer can understand the full domain in under 5 minutes.
