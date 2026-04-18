# pet.insurance.domain.app.v1

A **spec-driven, contract-first Pet Insurance REST API** built with Python/FastAPI.

Pet owners can register their pets and submit insurance claims. Agents review, approve, or reject claims.

> **Full documentation:** [`docs/index.md`](docs/index.md)

---

## Quick Start

```bash
task api:install   # install Python dependencies
task api:test      # run all tests
task lint          # lint OpenAPI + AsyncAPI contracts
task domain:check  # lint + test in one step
```

To run the API server locally:

```bash
task api:dev       # start Uvicorn with hot reload (port 3000)
```

Then exercise the full domain via the demo workflow:

```bash
task api:demo      # run the end-to-end pet insurance demo
```

---

## Domain

### Roles

| Role | Description |
|------|-------------|
| `pet_owner` | Registers pets and submits/cancels claims |
| `agent` | Reviews and approves or rejects claims |

### Resources

| Resource | Path | Description |
|----------|------|-------------|
| Pets | `/v1/pets` | Register and manage pets |
| Claims | `/v1/claims` | Submit and manage insurance claims |

### Claim Status Lifecycle

```
pending ──► approved
pending ──► rejected
pending ──► [cancelled / removed]
```

---

## Architecture

- **Python/FastAPI** + Uvicorn
- **JWT authentication** (access + refresh tokens)
- **Role-based access control** (`pet_owner`, `agent`)
- **In-memory store** — resets on restart
- **Specs-first** — all routes and schemas derive from `docs/specifications/`

---

## Project Structure

```
api/
  src/
    main.py               # FastAPI app (CORS, rate limiting, routes)
    server.py             # Uvicorn entry point
    auth.py               # JWT sign/verify utilities
    store.py              # In-memory store (users, pets, claims)
    models.py             # Pydantic request/response models
    middleware/
      authenticate.py     # JWT dependency + require_role helper
    routes/
      auth.py             # Register, login, refresh, logout
      pets.py             # Register, list, view, edit, remove pets
      claims.py           # Submit, list, view, approve, reject, cancel claims
  tests/
    conftest.py           # Store reset fixture
    helpers.py            # create_pet_owner_token, create_agent_token, seed_pet, seed_claim
    test_auth.py          # Auth route tests
    test_pets.py          # Pets route tests
    test_claims.py        # Claims route tests
    test_contract.py      # Response shape / contract tests
docs/
  specifications/
    prd.md                # Product requirements
    domain-model.md       # Pet + Claim entity definitions
    auth-matrix.md        # Role-based access control rules
    sequence-diagrams.md  # Key interaction flows (Mermaid)
    contracts/
      openapi.yaml        # REST API contract
      asyncapi.yaml       # Domain event contract
```
