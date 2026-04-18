# Pet Insurance API

A spec-driven, contract-first **Pet Insurance REST API** built with Python/FastAPI.

Pet owners can register their pets and submit insurance claims for veterinary costs.
Insurance agents review, approve, or reject those claims.

---

## Specifications

All authoritative business requirements live in `docs/specifications/`.
**Code must conform to specs, not the other way around.**

| Document | Description |
|---|---|
| [Product Requirements](specifications/prd.md) | Problem statement, personas, user stories, goals |
| [Domain Model](specifications/domain-model.md) | Pet + Claim entities, relationships, claim lifecycle |
| [Auth Matrix](specifications/auth-matrix.md) | `pet_owner` and `agent` roles and access rules |
| [Sequence Diagrams](specifications/sequence-diagrams.md) | Key interaction flows (Mermaid) |
| [**Interactive API Reference →**](specifications/api-reference.html) | OpenAPI 3.0.3 contract — live try-it-out |
| [**AsyncAPI Event Reference →**](specifications/asyncapi-reference.html) | Domain event catalogue — CloudEvents schemas |

Raw contract files: [`specifications/contracts/openapi.yaml`](specifications/contracts/openapi.yaml) · [`specifications/contracts/asyncapi.yaml`](specifications/contracts/asyncapi.yaml)

---

## Tasks

All automation is in `Taskfile.yml` (project-wide) and `Taskfile.api.yml` (API-specific).
Always use `task` — never run raw `curl`, `pip`, or `spectral` directly.

```bash
task                # list all available tasks
task api:install    # install Python dependencies (pip)
task api:dev        # start dev server on http://localhost:3000
task api:test       # run all tests
task lint           # lint OpenAPI + AsyncAPI contracts
task domain:check   # lint + test in one step
task api:demo       # run the full end-to-end pet insurance demo
task docs:serve     # serve this documentation site locally
```

---

## Architecture

| Layer | Location | Description |
|-------|----------|-------------|
| Entry point | `api/server.py` | Starts the Uvicorn server |
| App config | `api/src/main.py` | CORS, rate limiting, routes, exception handling |
| Auth | `api/src/auth.py` · `api/src/middleware/authenticate.py` | JWT signing/verification and `require_role` dependency |
| Routes | `api/src/routes/auth.py` · `pets.py` · `claims.py` | Auth, pets, claims |
| Store | `api/src/store.py` | In-memory store — `users`, `pets`, `claims` dicts |
| Models | `api/src/models.py` | Pydantic request/response models |
| Tests | `api/tests/` | Per-route integration tests using `api/tests/helpers.py` |

---

## Key Principles

1. **Specs drive code.** If code and spec disagree, fix the code — not the spec.
2. **Do not edit `docs/specifications/` incidentally.** Spec changes are deliberate business decisions.
3. **Domain model is authoritative for naming.** Entity and attribute names must be used consistently across routes, tests, and store.
4. **Auth matrix is authoritative for access control.** All route and middleware logic must match it exactly.
5. **OpenAPI contract is authoritative for the REST API.** Paths, methods, request/response shapes, and status codes must match.
6. **Task-first.** Run `task` to discover commands. If no task exists for an operation, add one before running it.
7. **Business language over CRUD.** Prefer "register / submit / approve / reject / cancel / edit / remove" over "create / update / delete" in human-readable contexts.

---

## Domain Summary

### Roles

| Role | Can do |
|------|--------|
| `pet_owner` | Register pets, submit claims, view/cancel own claims |
| `agent` | View any pet, list/view all claims, approve/reject claims |

### Claim Status Lifecycle

```
pending ──► approved   (agent action)
pending ──► rejected   (agent action)
pending ──► [removed]  (pet owner cancels)
```

Approved and rejected are terminal states.
