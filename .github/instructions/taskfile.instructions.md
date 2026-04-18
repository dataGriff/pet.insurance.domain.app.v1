---
description: "Use when reading, writing, or adding tasks to Taskfile.yml or Taskfile.api.yml. Covers naming conventions, structure, when to add a new task, and how to avoid duplicate or ad-hoc commands."
applyTo: "Taskfile*.yml"
---

# Taskfile Conventions

## Taskfile locations

| File | Contains |
|------|----------|
| `Taskfile.yml` | Project-wide tasks: lint, docs, top-level `api:*` shortcuts that delegate to `Taskfile.api.yml` |
| `Taskfile.api.yml` | All API-specific tasks: server, auth, resources, demo workflow, state management |

New tasks belong in `Taskfile.api.yml` unless they are project-wide (linting, docs, CI helpers).

## Naming convention

Follow the existing `namespace:resource:action` pattern:

```
api:items:list          # list all items
api:items:get           # get a single item
api:items:create        # create an item
api:items:update        # update an item
api:auth:register:contributor
```

- Namespaces are lowercase, hyphen-separated (`line-items`, not `lineItems`)
- Use consistent verbs: `list`, `get`, `create`, `update`, `delete`, `start`, `complete`, `cancel`, `submit`, `accept`, `decline`, `send`
- Qualifier (e.g. a role name like `contributor`) goes last when disambiguating

## Required fields for every new task

Every task must have a `desc:` so it appears in `task --list`:

```yaml
my:new:task:
  desc: Brief description of what this task does
  cmds:
    - ...
```

## When to add a new task

Add a task whenever you would otherwise run a raw CLI command during development, CI, or demos:
- A new API endpoint needs to be exercised manually → add `api:<resource>:<action>`
- A new build step is introduced → add it to `Taskfile.yml`
- A script or tool is run more than once → it belongs in a task

**Do not** run raw `curl`, `npm`, `spectral`, `mkdocs`, or other CLI commands directly. Add a task first.

## State management (demo tasks)

Demo tasks that carry output to later steps use `.demo-state` as a key-value store:

```yaml
vars:
  STATE: .demo-state  # defined at the top of Taskfile.api.yml

# Reading a saved value:
vars:
  MY_ID:
    sh: grep '^MY_ID=' {{.STATE}} 2>/dev/null | cut -d= -f2-

# Writing a saved value:
cmds:
  - |
    grep -v "^MY_ID=" {{.STATE}} > {{.STATE}}.tmp 2>/dev/null || true
    echo "MY_ID=$VALUE" >> {{.STATE}}.tmp
    mv {{.STATE}}.tmp {{.STATE}}
```

Use `task api:state:clear` to reset state between demo runs.

## Checking for duplicates before adding

Before adding a task, run `task --list` to confirm no equivalent already exists. If a similar task exists, extend or alias it rather than creating a near-duplicate.
