---
description: "Use when bootstrapping a new business domain into this template repository. Covers the domain:init workflow, spec-first principles, and what to change vs what to keep."
applyTo: "docs/specifications/_template/**,Taskfile.yml"
---

# Domain Template — Bootstrap Guidelines

## Purpose

This repository is a **reusable template**. When instantiating it for a new business domain, follow this workflow precisely to ensure the specs-first approach is maintained.

## Bootstrap Workflow

### Step 1: Run `task domain:init`

```bash
task domain:init
```

This copies the blank spec templates from `docs/specifications/_template/` into `docs/specifications/` (without overwriting any existing files). Run with `FORCE=true` to overwrite:

```bash
task domain:init FORCE=true
```

### Step 2: Fill in the domain specifications (in order)

Edit the files in `docs/specifications/` in this recommended order:

1. **`prd.md`** — Define the problem, personas, and user stories first. This anchors everything else.
2. **`domain-model.md`** — Define entities, attributes, and relationships from the PRD.
3. **`auth-matrix.md`** — Define roles and access rules. Derive from PRD user stories.
4. **`sequence-diagrams.md`** — Define key interaction flows. Derive from PRD + domain model.
5. **`contracts/openapi.yaml`** — Define the REST API contract. Must match domain model + auth matrix.
6. **`contracts/asyncapi.yaml`** — Define domain events. Derive from state transitions in domain model.

### Step 3: Implement the API

With specs complete, implement the API to match:

- `api/src/store.js` — Replace example entities with your domain's entities
- `api/src/routes/` — Replace example routes with routes matching your OpenAPI spec
- `api/tests/` — Replace example tests with tests for your routes and auth matrix

### Step 4: Validate

```bash
task domain:check   # lint contracts + run all tests
```

## Key Rules During Bootstrap

1. **Fill specs completely before writing any code.** Code written before specs are complete will drift.
2. **Do not modify `docs/specifications/_template/`.** That directory is the reusable template pack — only edit the copies in `docs/specifications/`.
3. **Entity names in code must exactly match `domain-model.md`.** Do not invent synonyms.
4. **Every route must correspond to an operation in `openapi.yaml`.** No "extra" routes.
5. **Every access control check must correspond to a rule in `auth-matrix.md`.** No ad-hoc restrictions.

## What to Keep vs Replace

### Keep (template engine — do not change unless there is a clear reason):
- `api/src/app.js` — Express app setup (CORS, rate limiting, OpenAPI validation middleware)
- `api/src/auth.js` — JWT signing/verification utilities
- `api/src/middleware/authenticate.js` — JWT middleware and `requireRole` helper
- `api/src/middleware/errorHandler.js` — Centralised error handler
- `api/tests/helpers.js` — Token and store seeding helpers (extend, don't replace)
- `Taskfile.yml` — Project-wide tasks (add domain tasks here)
- `Taskfile.api.yml` — API-specific tasks (add resource tasks here)
- `.spectral-openapi.yaml`, `.spectral-asyncapi.yaml` — Linting rulesets
- `.github/` — CI workflows and Copilot instructions

### Replace (domain pack — this is what changes per project):
- `docs/specifications/` — All spec files (use `task domain:init` to start)
- `api/src/store.js` — Domain-specific in-memory entities
- `api/src/routes/` — Domain-specific route handlers
- `api/tests/*.test.js` (except `helpers.js`) — Domain-specific tests
- `README.md` — Project description
- `AGENTS.md` — Project-specific AI guidelines
- `docs/index.md` — Docs homepage
- `mkdocs.yml` — Site name, URL, repo name
- `api/package.json` — Package name and description

## When Working on Specs vs Code

- If asked to **change a spec file**: confirm this is a deliberate business decision. Spec changes ripple into code — do them intentionally.
- If asked to **change code that conflicts with a spec**: fix the code, not the spec. The spec wins.
- If **code and spec are both wrong**: flag it. Do not silently "fix" specs to match bad code.
