# domain-api-template

A **GitHub Template repository** for building spec-driven, contract-first REST APIs with Node.js/Express.
Write your specs first — then implement to match.

> **Full documentation:** [`docs/index.md`](docs/index.md) (also published as a [MkDocs site](https://datagriff.github.io/domain-api-template/)).

---

## Quick Start

```bash
# 1. Create a new repo from this template (click "Use this template" on GitHub)
# 2. Then:
task api:install        # install dependencies
task domain:init        # copy blank spec templates into docs/specifications/
# 3. Edit files in docs/specifications/ for your domain
task domain:check       # lint contracts + run all tests
```

See [`docs/index.md`](docs/index.md) for the full architecture overview, task reference, key principles, and bootstrap guide.

---

## New Domain Checklist

- [ ] Create repo from template ("Use this template" on GitHub)
- [ ] Update `api/package.json` name/description and `mkdocs.yml` site name
- [ ] `task api:install`
- [ ] `task domain:init`
- [ ] Fill in `docs/specifications/prd.md`
- [ ] Fill in `docs/specifications/domain-model.md`
- [ ] Fill in `docs/specifications/auth-matrix.md`
- [ ] Fill in `docs/specifications/sequence-diagrams.md`
- [ ] Fill in `docs/specifications/contracts/openapi.yaml`
- [ ] Fill in `docs/specifications/contracts/asyncapi.yaml`
- [ ] Update `api/src/store.js` with domain entities
- [ ] Replace `api/src/routes/` with domain routes
- [ ] Replace `api/tests/` with domain tests
- [ ] `task domain:check` — all green ✓
- [ ] Update `README.md`, `AGENTS.md`, and `docs/index.md` for your domain
- [ ] Enable "Template repository" in GitHub Settings if reusing as a template

---

## What's in the Box

| Area | Location | Keep or replace? |
|------|----------|-----------------|
| Express app setup | `api/src/app.js` | **Keep** |
| JWT auth + middleware | `api/src/auth.js`, `api/src/middleware/` | **Keep** |
| Error handler | `api/src/middleware/errorHandler.js` | **Keep** |
| Test helpers | `api/tests/helpers.js` | Extend |
| Taskfiles | `Taskfile.yml`, `Taskfile.api.yml` | Extend |
| Spec linting | `.spectral-openapi.yaml`, `.spectral-asyncapi.yaml` | **Keep** |
| CI workflows | `.github/workflows/` | **Keep** |
| AI guidelines | `.github/instructions/`, `AGENTS.md` | Update for your domain |
| **Items example** | `api/src/routes/items.js`, `api/src/store.js`, `api/tests/`, `docs/specifications/` | **Replace** |
| Blank spec templates | `docs/specifications/_template/` | **Keep** (source for `domain:init`) |

---

## GitHub Template Repository

To enable the **Use this template** button on a fork:

1. Go to **Settings → General**
2. Check **Template repository**
