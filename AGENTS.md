# Domain API Template — Agent Workspace Instructions

> **Navigation and documentation:** see [`docs/index.md`](docs/index.md).
> It is the single source of truth for spec links, task commands, architecture, key principles, and the bootstrap workflow.

---

## Core Rules

1. **Specs drive code.** If code diverges from a spec, fix the code — not the spec. Only change a spec when there is a deliberate business decision to do so.
2. **Do not edit `docs/specifications/` incidentally.** Spec changes require explicit intent and should be reviewed separately from code changes.
3. **Domain model is authoritative for naming.** Entity names, attribute names, and relationship names defined in `docs/specifications/domain-model.md` must be used consistently in code (routes, store, tests, variables).
4. **Auth matrix is authoritative for access control.** All authorization logic in `api/middleware/` and route handlers must match `docs/specifications/auth-matrix.md` exactly.
5. **OpenAPI contract is authoritative for the REST API.** Request/response shapes, status codes, and route paths must match `docs/specifications/contracts/openapi.yaml`.
6. **Task-first rule.** Always run `task` to discover available tasks before running any raw commands. If no task exists for an operation, add one before running it.
7. **Business language over CRUD.** Use domain verbs in specs, user stories, descriptions, and comments. Prefer "add / edit / remove / archive" over "create / update / delete" in any human-readable context.

---

## Architecture

- **API**: Node.js/Express in `api/`. Entry point `api/src/server.js`, app config `api/src/app.js`.
- **Auth**: JWT-based. Middleware in `api/src/middleware/authenticate.js`.
- **Routes**: One file per resource in `api/src/routes/`.
- **Store**: In-memory store in `api/src/store.js` (no database).
- **Tests**: Per-route test files in `api/tests/`. Use helpers from `api/tests/helpers.js`.

---

## Build and Test

All commands must be run via `task`. See [`docs/index.md`](docs/index.md#tasks) for the full task reference.

```bash
task               # list all available tasks
task api:install   # install dependencies
task api:test      # run all tests
task lint          # lint OpenAPI + AsyncAPI contracts
task domain:check  # lint + test in one step
task api:demo      # run the full end-to-end demo
task docs:serve    # serve docs locally
```

---

## Detailed Per-Area Instructions

The `.github/instructions/` directory contains file-scoped rules that GitHub Copilot loads automatically. Other agents should read these manually when working on matching areas:

| File | Read when working on |
|------|----------------------|
| `.github/instructions/specs.instructions.md` | Anything in `docs/specifications/` |
| `.github/instructions/api-implementation.instructions.md` | Anything in `api/` |
| `.github/instructions/taskfile.instructions.md` | `Taskfile.yml` or `Taskfile.api.yml` |
| `.github/instructions/domain-template.instructions.md` | Bootstrapping a new domain |
