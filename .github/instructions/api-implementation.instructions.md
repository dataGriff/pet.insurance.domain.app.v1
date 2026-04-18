---
description: "Use when writing, editing, or reviewing API code, routes, middleware, tests, or store logic. Ensures implementation conforms to the authoritative business specifications in docs/specs/."
applyTo: "api/**"
---

# API Implementation — Spec Conformance Rules

Before writing or modifying any code in `api/`, check the relevant spec documents. Specs always win.

## Mandatory checks before implementing

| What you're changing | Check this spec first |
|---------------------|-----------------------|
| Route path, method, request/response shape, status code | [`docs/specifications/contracts/openapi.yaml`](../../docs/specifications/contracts/openapi.yaml) |
| Access control, role restrictions, authentication requirements | [`docs/specifications/auth-matrix.md`](../../docs/specifications/auth-matrix.md) |
| Entity names, field names, relationships, business rules | [`docs/specifications/domain-model.md`](../../docs/specifications/domain-model.md) |
| Interaction ordering, preconditions, side effects | [`docs/specifications/sequence-diagrams.md`](../../docs/specifications/sequence-diagrams.md) |

## Naming

All entity names, attribute names, and relationship names must exactly match `docs/specs/domain-model.md`. Do not invent synonyms or rename things (e.g. use the exact entity name from the domain model, not an alias).

## Access control

Every route's authentication and role checks must exactly match `docs/specs/auth-matrix.md`. The middleware is in `api/src/middleware/authenticate.js`. Never widen access beyond what the matrix permits.

## REST contract

Route paths, HTTP methods, request bodies, query parameters, and response schemas must match `docs/specs/contracts/openapi.yaml`. Do not add or remove fields without a corresponding spec change.

## Tests

Each route file has a corresponding test file in `api/tests/`. Tests should cover the access control rules from `docs/specs/auth-matrix.md` — use helpers from `api/tests/helpers.js`.

## Business language

Prefer business language over CRUD terminology everywhere it appears in human-readable contexts — descriptions, comments, test labels, error messages, and spec documents. Use the language of the domain (e.g. "add", "edit", "remove", "archive") rather than generic database operations ("create", "update", "delete"). HTTP methods (POST/PATCH/DELETE) and technical identifiers (`operationId`, `store.items.delete()`) can keep their technical names.
