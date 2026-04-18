# Domain API Template

A spec-driven, contract-first REST API template for Node.js/Express.
Write your specs first — then implement. The **Items** example domain shows every pattern in action.

---

## Specifications

All authoritative business requirements live in `docs/specifications/`.
**Code must conform to specs, not the other way around.**

| Document | Description |
|---|---|
| [Product Requirements](specifications/prd.md) | Problem statement, personas, user stories, goals |
| [Domain Model](specifications/domain-model.md) | Entities, attributes, relationships, business rules |
| [Auth Matrix](specifications/auth-matrix.md) | Roles and which operations each role may perform |
| [Sequence Diagrams](specifications/sequence-diagrams.md) | Key interaction flows (Mermaid) |
| [**Interactive API Reference →**](specifications/api-reference.html) | OpenAPI 3.0.3 contract — live try-it-out |
| [**AsyncAPI Event Reference →**](specifications/asyncapi-reference.html) | Domain event catalogue — CloudEvents schemas |

Raw contract files: [`specifications/contracts/openapi.yaml`](specifications/contracts/openapi.yaml) · [`specifications/contracts/asyncapi.yaml`](specifications/contracts/asyncapi.yaml)

---

## Tasks

All automation is in `Taskfile.yml` (project-wide) and `Taskfile.api.yml` (API-specific).
Always use `task` — never run raw `npm`, `curl`, or `spectral` directly.

```bash
task                # list all available tasks
task api:install    # install npm dependencies
task api:dev        # start dev server on http://localhost:3000
task api:test       # run all tests
task lint           # lint OpenAPI + AsyncAPI contracts
task domain:check   # lint + test in one step
task domain:init    # seed blank spec templates into docs/specifications/
task api:demo       # run the full end-to-end demo
task docs:serve     # serve this documentation site locally
```

---

## Architecture

| Layer | Location | Description |
|-------|----------|-------------|
| Entry point | `api/src/server.js` | Starts the Express server |
| App config | `api/src/app.js` | CORS, rate limiting, OpenAPI validation middleware |
| Auth | `api/src/auth.js` · `api/src/middleware/authenticate.js` | JWT signing/verification and `requireRole` helper |
| Routes | `api/src/routes/` | One file per resource |
| Store | `api/src/store.js` | In-memory store (no database) |
| Error handling | `api/src/middleware/errorHandler.js` | Centralised error handler |
| Tests | `api/tests/` | Per-route integration tests using `api/tests/helpers.js` |

---

## Key Principles

1. **Specs drive code.** If code and spec disagree, fix the code — not the spec.
2. **Do not edit `docs/specifications/` incidentally.** Spec changes are deliberate business decisions.
3. **Domain model is authoritative for naming.** Entity and attribute names defined here must be used consistently across routes, tests, and store.
4. **Auth matrix is authoritative for access control.** All route and middleware logic must match it exactly.
5. **OpenAPI contract is authoritative for the REST API.** Paths, methods, request/response shapes, and status codes must match.
6. **Task-first.** Run `task` to discover commands. If no task exists for an operation, add one before running it.
7. **Business language over CRUD.** Use domain verbs in specs, user stories, descriptions, and comments. Prefer "add / edit / remove / archive" over "create / update / delete" in any human-readable context. HTTP methods and technical identifiers keep their technical names.

---

## Example Domain: Items

The included example is a minimal **Items catalogue** — two roles and one resource — generic enough to learn from without domain noise:

- **2 roles**: `contributor` (add/edit/remove own items) · `viewer` (read-only)
- **1 resource**: `items` (id, name, description, status, contributorId, createdAt, updatedAt)
- Authentication: register, login, refresh token, logout (JWT)

This example demonstrates auth, RBAC, item lifecycle, ownership rules, pagination, and domain events end-to-end.
Replace it entirely when you instantiate the template for a real domain.

---

## Bootstrap a New Domain

1. Create a new repo from this template (**Use this template** on GitHub)
2. `task api:install`
3. `task domain:init` — copies blank spec templates into `docs/specifications/`
4. Fill in each spec file (start with `prd.md`, then `domain-model.md`, `auth-matrix.md`, `sequence-diagrams.md`, finally the contracts)
5. Update `api/src/store.js` with your domain's entities
6. Replace `api/src/routes/` and `api/tests/` with your domain's routes and tests
7. `task domain:check` — all green ✓
8. Update `README.md`, `AGENTS.md`, and this file (`docs/index.md`) for your domain
