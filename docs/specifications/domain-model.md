# Domain Model — Items

> **Example domain.** This is the working reference implementation included with the Domain API Template.
> Replace this file with your own domain model by running `task domain:init`.

---

## Overview

The **Items** domain is a minimal catalogue of named items. Each item is owned by a contributor and has a simple `active` / `archived` lifecycle. There are two roles: `contributor` (creates and manages items) and `viewer` (read-only access).

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
| `role` | enum | Yes | `contributor` or `viewer` |
| `createdAt` | ISO 8601 | Yes | Registration timestamp |

**Business Rules:**
- Email must be unique across all users.
- Password is stored as a bcrypt hash; never returned in API responses.
- Role is set at registration and cannot be changed via the API.

---

### Item

Represents a named entry in the catalogue, owned by a contributor.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | UUID | Yes | Unique identifier |
| `name` | string | Yes | Display name (min 1 char) |
| `description` | string \| null | No | Optional longer description |
| `status` | enum | Yes | `active` or `archived` |
| `contributorId` | UUID | Yes | ID of the user who created this item |
| `createdAt` | ISO 8601 | Yes | Creation timestamp |
| `updatedAt` | ISO 8601 | Yes | Last update timestamp |

**Business Rules:**
- `status` defaults to `active` on creation.
- Only the contributor who added an item may edit or remove it.
- Viewers may list and view any item but cannot modify them.

---

## Relationships

```
User (role=contributor) ──── creates many ──── Item
Item ──── belongs to ──────────────────────── User (contributorId)
```

---

## Aggregates

| Aggregate Root | Entities Contained | Description |
|---------------|-------------------|-------------|
| `Item` | Item | Self-contained; ownership is tracked via `contributorId` |
| `User` | User | Self-contained; no nested child entities |

---

## Domain Events

| Event | Trigger | Channel |
|-------|---------|---------|
| `ItemAdded` | POST /v1/items → 201 | `items.item.added` |
| `ItemEdited` | PATCH /v1/items/{itemId} → 200 | `items.item.edited` |
| `ItemRemoved` | DELETE /v1/items/{itemId} → 204 | `items.item.removed` |

---

## Status Lifecycle

### Item Status

```
active ⟷ archived
```

| From | To | Trigger |
|------|----|---------|
| `active` | `archived` | PATCH /v1/items/{itemId} with `status: "archived"` |
| `archived` | `active` | PATCH /v1/items/{itemId} with `status: "active"` |

Items can be toggled between `active` and `archived` freely by their owner contributor.
