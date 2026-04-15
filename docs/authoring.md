# Authoring Guide

How to add new atoms to `gobiq-knowledge`.

## Before you start

1. Read [`content_types.md`](content_types.md) to pick the right atom type.
2. Search existing atoms — if your idea is already covered, **edit** instead of
   creating a duplicate. Use `related:` edges for cross-references.
3. Pull `main` and create a feature branch.

## Step-by-step

### 1. Create the folder + `_node.yaml`

Folder lives under `knowledge/{type}/{id}/`. The `id:` must match the folder
path exactly (dot-separated). Example for a new concept:

```
knowledge/concepts/market_share/
├── _node.yaml
└── content.md
```

`_node.yaml`:

```yaml
id: "concepts.market_share"
name: "Market Share"
description: "% of category offtake captured by a brand, partitioned by platform × period."
type: concept
parent: null
related:
  - id: "concepts.osa"
    relation: feeds_into
    label: "OSA drops can cause market share losses"
primitives: [availability]   # or visibility / pricing
common_questions:
  - "What is market share?"
  - "How is market share calculated?"
planner_hint: >-
  Use when the user asks for the definition of market share or how it's computed
  across platforms.
expose_to_planner: true
```

### 2. Write the `content.md`

Use the template for your atom type — see [`content_types.md`](content_types.md).

Keep it tight. One concept per atom. If you find yourself documenting two
metrics in one file, split them.

### 3. Add bidirectional relations

If you reference another atom, **add the back-reference too**. Open the related
atom's `_node.yaml` and add the reverse edge. The CI bidirectional check
will fail your PR if you skip this.

### 4. Run validators locally

```bash
pip install -e ".[dev]"
pytest
```

All three test suites must pass:
- `test_schema.py` — schema validates
- `test_references.py` — refs resolve, relations are symmetric
- `test_traversals.py` — procedures terminate

### 5. Update `CHANGELOG.md`

Add an entry under `[Unreleased]`. Be specific about what was added.

### 6. Open a PR

CI re-runs all checks. PR cannot merge if any fail.

### 7. Bump version on merge

Once merged to `main`:
- Patch (most content edits): `0.X.Y → 0.X.Y+1`
- Minor (new atom type, procedure, output spec): `0.X.0 → 0.X+1.0`
- Major (schema break): `X.0.0 → X+1.0.0`

Tag the release: `git tag v0.1.1 && git push --tags`. CI publishes.

## Anti-patterns

- **Writing decision trees inside `content.md`.** Use a `procedure` atom.
- **Putting thresholds inside `concept` atoms.** Make a `threshold` atom and
  link via `uses_threshold`.
- **Copying SQL into multiple recipes.** Extract the shared SQL fragment into
  a `detection` atom and reference it.
- **Skipping `related:` because "it's obvious."** Future authors don't have
  your context. Make it explicit.
- **Creating a new `domain/` for one topic.** Topics live under existing
  domains. Adding a new domain requires updating `domains/_node.yaml`.

## Getting reviewed

- Schema validators are not enough. Have a domain expert review the `content.md`.
- For new procedures, walk through the traversal verbally with a strategist —
  does the decision tree match how they actually diagnose this?
- For new recipes, confirm the SQL works against the actual Snowflake schema.
