# Sequence Diagrams — Items

> **Example domain.** This is the working reference implementation included with the Domain API Template.
> Replace this file with your own sequence diagrams by running `task domain:init`.

---

## Flow 1: Register and Log In

```mermaid
sequenceDiagram
    participant Client
    participant API

    Client->>API: POST /v1/auth/register<br/>{ email, password, role: "contributor" }
    API-->>Client: 201 { accessToken, refreshToken, user }

    Client->>API: POST /v1/auth/login<br/>{ email, password }
    API-->>Client: 200 { accessToken, refreshToken, user }
```

---

## Flow 2: Contributor Creates and Manages Items

```mermaid
sequenceDiagram
    participant Contributor
    participant API

    Contributor->>API: POST /v1/items<br/>{ name: "My Item" }<br/>Authorization: Bearer <token>
    API-->>Contributor: 201 { id, name, status: "active", contributorId, ... }

    Contributor->>API: GET /v1/items<br/>Authorization: Bearer <token>
    API-->>Contributor: 200 { data: [...], pagination: { page, pageSize, total } }

    Contributor->>API: PATCH /v1/items/{itemId}<br/>{ status: "archived" }<br/>Authorization: Bearer <token>
    API-->>Contributor: 200 { id, name, status: "archived", ... }

    Contributor->>API: DELETE /v1/items/{itemId}<br/>Authorization: Bearer <token>
    API-->>Contributor: 204
```

---

## Flow 3: Viewer Browses Items

```mermaid
sequenceDiagram
    participant Viewer
    participant API

    Viewer->>API: POST /v1/auth/login<br/>{ email, password }
    API-->>Viewer: 200 { accessToken, ... }

    Viewer->>API: GET /v1/items<br/>Authorization: Bearer <token>
    API-->>Viewer: 200 { data: [...], pagination: { ... } }

    Viewer->>API: GET /v1/items/{itemId}<br/>Authorization: Bearer <token>
    API-->>Viewer: 200 { id, name, description, status, ... }

    Viewer->>API: POST /v1/items<br/>{ name: "Viewer Item" }<br/>Authorization: Bearer <token>
    API-->>Viewer: 403 { code: "FORBIDDEN" }
```

---

## Flow 4: Token Refresh

```mermaid
sequenceDiagram
    participant Client
    participant API

    Note over Client: Access token has expired

    Client->>API: POST /v1/auth/refresh<br/>{ refreshToken }
    API-->>Client: 200 { accessToken, refreshToken }

    Client->>API: GET /v1/items<br/>Authorization: Bearer <new_token>
    API-->>Client: 200 { data: [...] }
```

---

## Notes

- All authenticated requests include `Authorization: Bearer <token>` (omitted from some diagrams for brevity).
- `4xx` error paths are covered by the auth matrix — see `auth-matrix.md`.
