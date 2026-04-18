# Sequence Diagrams — Pet Insurance

---

## Overview

Key interaction flows for the Pet Insurance domain.

All authenticated requests include `Authorization: Bearer <token>` header (omitted from diagrams for brevity). `4xx` error paths are omitted; see `auth-matrix.md` for access control rules.

---

## Flow 1: Registration and Login

```mermaid
sequenceDiagram
    participant Client
    participant API

    Client->>API: POST /v1/auth/register (email, password, role: pet_owner)
    API-->>Client: 201 { accessToken, refreshToken, user }

    Client->>API: POST /v1/auth/login (email, password)
    API-->>Client: 200 { accessToken, refreshToken, user }
```

---

## Flow 2: Pet Owner Registers a Pet and Submits a Claim

```mermaid
sequenceDiagram
    participant PetOwner as Pet Owner
    participant API

    PetOwner->>API: POST /v1/pets (name, species, breed, dateOfBirth)
    API-->>PetOwner: 201 { id, name, species, ... petOwnerId }

    PetOwner->>API: POST /v1/claims (petId, amount, description)
    API-->>PetOwner: 201 { id, petId, amount, status: "pending", ... }

    PetOwner->>API: GET /v1/claims
    API-->>PetOwner: 200 { data: [{ id, status: "pending", ... }], pagination }
```

---

## Flow 3: Agent Reviews and Approves a Claim

```mermaid
sequenceDiagram
    participant Agent
    participant API

    Agent->>API: GET /v1/claims
    API-->>Agent: 200 { data: [{ id, status: "pending", petId, amount, ... }], pagination }

    Agent->>API: GET /v1/pets/{petId}
    API-->>Agent: 200 { id, name, species, dateOfBirth, ... }

    Agent->>API: POST /v1/claims/{claimId}/approve
    API-->>Agent: 200 { id, status: "approved", ... }
```

---

## Flow 4: Agent Rejects a Claim

```mermaid
sequenceDiagram
    participant Agent
    participant API

    Agent->>API: POST /v1/claims/{claimId}/reject
    API-->>Agent: 200 { id, status: "rejected", ... }
```

---

## Flow 5: Pet Owner Cancels a Pending Claim

```mermaid
sequenceDiagram
    participant PetOwner as Pet Owner
    participant API

    PetOwner->>API: DELETE /v1/claims/{claimId}
    API-->>PetOwner: 204 (No Content)
```

---

## Flow 6: Token Refresh

```mermaid
sequenceDiagram
    participant Client
    participant API

    Client->>API: POST /v1/auth/refresh (refreshToken)
    API-->>Client: 200 { accessToken, refreshToken }
```
