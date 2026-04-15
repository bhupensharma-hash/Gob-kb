# Atom Types

The 11 atom types in `gobiq-knowledge`, what they're for, and what their
`content.md` should contain.

## Quick reference table

| Type | Purpose | Lives in | Exposed to planner? |
|---|---|---|---|
| `global` | Always-loaded content | `knowledge/global/` | `false` |
| `category` | Organizational grouping (no own content) | `knowledge/{type}/_node.yaml` | `false` |
| `chat_template` | Chat-layer template | `knowledge/chat_templates/` | `true` |
| `domain` | Major analytics domain | `knowledge/domains/{domain}/` | `true` |
| `topic` | Specific topic within a domain | `knowledge/domains/{domain}/{topic}/` | `true` |
| `playbook` | Typed traversal (decision tree) | `knowledge/playbooks/` | `true` |
| `metric` | Metric definition + formula | `knowledge/metrics/` | `true` |
| `diagnostic` | SQL fragment + threshold for a pattern | `knowledge/diagnostics/` | `true` |
| `benchmark` | Value bands for a metric | `knowledge/benchmarks/` | `true` |
| `report_section` | Report section spec (report assembler only) | `knowledge/report_sections/` | `false` |
| `recipe` | RAG-indexed Q→Action pair | inside `knowledge/recipes/*.md` | n/a |

## Detailed specs

### `metric`

**What it holds:** the definition + formula of one metric.

`content.md` template:

```markdown
# {Metric Name}

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

### `diagnostic`

**What it holds:** SQL fragment + threshold that identifies a pattern (transfer
issue, missing PO, etc.).

Required `_node.yaml` field: `sql:` (the SQL fragment).

`content.md` template:

```markdown
# {Diagnostic Name}

## What it identifies
[The pattern this diagnostic catches]

## Detection conditions
[Bullet list of all conditions that must be true]

## Threshold formula explained
[Why the thresholds are what they are]

## Loss extrapolation
[How to convert the diagnostic into a ₹ loss number]

## Ownership
[Who owns the fix]

## Typical root causes
[What causes this pattern]
```

### `benchmark`

**What it holds:** value bands for classifying a metric (healthy / warning / critical).

Required `_node.yaml` field: `thresholds:` (list of bands).

`content.md` template:

```markdown
# {Benchmark Name}

## Bands
[Table: band, range, color, action]

## Category-specific overrides
[Where the defaults don't apply]

## Interpretation rules
[How to apply these in practice]
```

### `playbook`

**What it holds:** a typed traversal — a decision tree expressed as a
sequence of steps that reference other atoms.

Required `_node.yaml` field: `traversal:` (list of typed steps).

Step types:
- `render` — render an atom into the output (ref required)
- `fetch_data` — run a recipe / SQL to get real values (consumer evaluates)
- `run_diagnostic` — run a diagnostic rule (returns true/false)
- `branch` — if/else (with `if_true:` and `if_false:` arms)
- `call_playbook` — recursive call (ref required)
- `terminate` — end the traversal (with verdict template)

`content.md` template:

```markdown
# {Playbook Name}

## Mindset
[How the analyst should think about this]

## The decision tree (high level)
[ASCII diagram of the tree]

## How chat consumes this
[What the user sees per turn]

## How report consumes this
[What the user sees in the report section]
```

### `report_section`

**What it holds:** which playbooks compose into which report sections, in
what order, with what CSS framework. Consumed only by the report assembler.

Required `_node.yaml` field: `sections:` (ordered list of section specs).

`content.md` template:

```markdown
# {Section Name} — Report Section Spec

## Composition
[Which playbooks this section walks]

## Style guide for this section
[Section-specific narration rules — owner attribution, headline first, etc.]

## Render flow
[Step-by-step what the assembler does]
```

### `domain` and `topic`

These match GoBIQ's existing structure exactly. See
[`/knowledge/domains/README.md`](../knowledge/domains/README.md).

### `chat_template`

Chat-layer templates for question patterns. See
[`/knowledge/chat_templates/README.md`](../knowledge/chat_templates/README.md).

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
