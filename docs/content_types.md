# Atom Types

The 11 atom types in `gobiq-knowledge`, what they're for, and what their
`content.md` should contain.

## Quick reference table

| Type | Purpose | Lives in | Exposed to planner? |
|---|---|---|---|
| `global` | Always-loaded content | `knowledge/global/` | `false` |
| `category` | Organizational grouping (no own content) | `knowledge/{type}/_node.yaml` | `false` |
| `template` | Chat-layer template | `knowledge/templates/` | `true` |
| `domain` | Major analytics domain | `knowledge/domains/{domain}/` | `true` |
| `topic` | Specific topic within a domain | `knowledge/domains/{domain}/{topic}/` | `true` |
| `procedure` | Typed traversal (decision tree) | `knowledge/procedures/` | `true` |
| `concept` | Metric or term definition | `knowledge/concepts/` | `true` |
| `detection` | SQL fragment + threshold for a pattern | `knowledge/detections/` | `true` |
| `threshold` | Value bands for a metric | `knowledge/thresholds/` | `true` |
| `output_spec` | Report section spec (report assembler only) | `knowledge/output_specs/` | `false` |
| `recipe` | RAG-indexed Q→Action pair | inside `knowledge/recipes/*.md` | n/a |

## Detailed specs

### `concept`

**What it holds:** the definition + formula of one metric or term.

`content.md` template:

```markdown
# {Concept Name}

## Definition
[1-2 sentences explaining what this is]

## Formula
[SQL or math expression with column-name references]

## Variants
[Table of variants — weighted vs raw, listed-only vs all, etc.]

## Source columns
[Which Snowflake tables/columns this is computed from]

## Common pitfalls
[Things that go wrong when computing this]
```

### `detection`

**What it holds:** SQL fragment + threshold that identifies a pattern (transfer
issue, missing PO, etc.).

Required `_node.yaml` field: `sql:` (the SQL fragment).

`content.md` template:

```markdown
# {Detection Name}

## What it identifies
[The pattern this detection catches]

## Detection conditions
[Bullet list of all conditions that must be true]

## Threshold formula explained
[Why the thresholds are what they are]

## Loss extrapolation
[How to convert the detection into a ₹ loss number]

## Ownership
[Who owns the fix]

## Typical root causes
[What causes this pattern]
```

### `threshold`

**What it holds:** value bands for classifying a metric (healthy / warning / critical).

Required `_node.yaml` field: `thresholds:` (list of bands).

`content.md` template:

```markdown
# {Threshold Name}

## Bands
[Table: band, range, color, action]

## Category-specific overrides
[Where the defaults don't apply]

## Interpretation rules
[How to apply these in practice]
```

### `procedure`

**What it holds:** a typed traversal — a decision tree expressed as a
sequence of steps that reference other atoms.

Required `_node.yaml` field: `traversal:` (list of typed steps).

Step types:
- `render` — render an atom into the output (ref required)
- `fetch_data` — run a recipe / SQL to get real values (consumer evaluates)
- `run_detection` — run a detection rule (returns true/false)
- `branch` — if/else (with `if_true:` and `if_false:` arms)
- `call_procedure` — recursive call (ref required)
- `terminate` — end the traversal (with verdict template)

`content.md` template:

```markdown
# {Procedure Name}

## Mindset
[How the analyst should think about this]

## The decision tree (high level)
[ASCII diagram of the tree]

## How chat consumes this
[What the user sees per turn]

## How report consumes this
[What the user sees in the report section]
```

### `output_spec`

**What it holds:** which procedures compose into which report sections, in
what order, with what CSS framework. Consumed only by the report assembler.

Required `_node.yaml` field: `sections:` (ordered list of section specs).

`content.md` template:

```markdown
# {Section Name} — Report Section Spec

## Composition
[Which procedures this section walks]

## Style guide for this section
[Section-specific narration rules — owner attribution, headline first, etc.]

## Render flow
[Step-by-step what the assembler does]
```

### `domain` and `topic`

These match GoBIQ's existing structure exactly. See
[`/knowledge/domains/README.md`](../knowledge/domains/README.md).

### `template`

Chat-layer templates for question patterns. See
[`/knowledge/templates/README.md`](../knowledge/templates/README.md).

### `global`

Always-loaded content. Multiple `global` atoms are concatenated in load order.
Today: only `global.narration_rules`.

### `recipe`

Lives inside `knowledge/recipes/*.md` files, not as a folder. Format:

```text
{Question}

==> **Execute X**: {instructions}


{Next question}

==> ...
```

Triple-newline separator. Parsed by `gobiq_knowledge.rag`.
