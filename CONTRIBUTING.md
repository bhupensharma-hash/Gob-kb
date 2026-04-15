# Contributing to gobiq-knowledge

This repo is the single source of truth for GoBIQ's analytical knowledge. Both the chat and report systems depend on it. Treat changes accordingly.

## Quick reference — adding new content

| Want to add... | Do this |
|---|---|
| A new metric definition | Create `knowledge/concepts/{metric_id}/` with `_node.yaml` (type: `concept`) + `content.md` |
| A new detection rule | Create `knowledge/detections/{rule_id}/` (type: `detection`) — SQL fragment + threshold |
| A new threshold band | Create `knowledge/thresholds/{name}/` (type: `threshold`) |
| A new domain topic | Create `knowledge/domains/{domain}/{topic}/` (type: `topic`) |
| A new decision tree / playbook | Create `knowledge/procedures/{procedure_id}/` (type: `procedure`) — references atoms by ID in `traversal:` |
| A new RAG recipe | Append to `knowledge/recipes/{domain}_recipes.md` using `Q\n\n==> Execute X: ...` format with triple-newline separator |
| A new chat template | Create `knowledge/templates/{template_id}/` (type: `template`) |
| A new report section | Create `knowledge/output_specs/{section_id}/` (type: `output_spec`) |

## The contract

Every node folder has exactly two files:

```
knowledge/concepts/osa/
├── _node.yaml      ← typed metadata (id, type, parent, related, etc.)
└── content.md      ← the actual knowledge (free-form markdown)
```

The `_node.yaml` is machine-validated. The `content.md` is consumed by assemblers.

## Authoring an atom

### 1. Pick the atom type

See [`docs/content_types.md`](docs/content_types.md) for what each type is for.

### 2. Create the folder + `_node.yaml`

The `id:` must match the folder path (dot-separated):

```yaml
id: "concepts.osa"
name: "On-Shelf Availability (OSA)"
description: "% of times a SKU is available across all stores it's listed in."
type: concept
parent: "concepts"
related:
  - id: "concepts.psl"
    relation: feeds_into
    label: "OSA gaps drive PSL"
  - id: "thresholds.osa_health"
    relation: cross_check
    label: "Apply this threshold to classify OSA values"
primitives: [availability]
common_questions:
  - "What is OSA?"
  - "How is on-shelf availability calculated?"
expose_to_planner: true
```

### 3. Write the `content.md`

Use the right template for the atom type — see [`docs/content_types.md`](docs/content_types.md).

### 4. Update related nodes

Relations are bidirectional. If A says `related: B`, B must say `related: A`. The reference checker enforces this.

### 5. Run validation locally

```bash
pytest tests/
```

This runs:
- Schema validation (every `_node.yaml` parses, has required fields)
- Reference checks (every parent/child/related ID resolves)
- Traversal checks (procedures terminate, no cycles)
- Bidirectional relation check

### 6. Open a PR

CI will re-run all checks. PRs cannot merge if any fail.

## Versioning your change

When your PR merges:

- **Patch** (most content edits, new individual atoms) — bump `0.x.Y`
- **Minor** (new atom type, new procedure, new output spec) — bump `0.X.0`
- **Major** (schema breaks, atom rename, loader API change) — bump `X.0.0`

Apps will need to update their pinned version to pick up your change.

## What NOT to do

- Don't edit two atoms to say the same thing — use a `related:` edge instead
- Don't write decision trees inside `content.md` — use a `procedure` atom with `traversal:`
- Don't put thresholds in concept atoms — make them their own `threshold` atoms so they can be reused
- Don't copy SQL into multiple recipes — extract the shared part into a recipe and reference it
- Don't skip `bidirectional` relations — the validator will fail your PR
