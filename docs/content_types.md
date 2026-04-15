# Atom Types

The 12 atom types in `gobiq-knowledge`, what they're for, and what their
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
| `metric_relationship` | Causal link between two metrics | `knowledge/metric_relationships/` | `true` |
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

### `metric_relationship`

**What it holds:** the causal link between two metrics — direction,
mechanism, elasticity, confidence, caveats. Authored when the relationship has
substance worth standalone documentation (used by playbooks, quoted in
reports). For obvious one-off links, just use a `causes` edge between metric
atoms instead of authoring a full relationship atom.

Required `_node.yaml` fields:
- `source_metric` — atom ID of the driving metric
- `target_metric` — atom ID of the driven metric
- `direction` — one of `increase_causes_increase`, `decrease_causes_increase`, `decrease_causes_decrease`, `increase_causes_decrease`
- `mechanism_short` — one-sentence WHY the link exists

Optional fields:
- `elasticity` — quantitative rule of thumb (formula or descriptive)
- `formula` — explicit math when applicable
- `confidence` — `high` / `medium` / `low`
- `caveats` — list of failure modes

`content.md` template:

```markdown
# {Source} → {Target} Causal Link

## What this captures
[Why this relationship matters in a sentence or two]

## Direction
[Increase causes increase / decrease causes increase / etc.]

## Mechanism
[The real-world WHY — what causes the link to exist]

## Elasticity (rule of thumb)
[Worked example showing how to apply the elasticity number]

## Confidence
[high/medium/low + brief justification]

## Caveats (when the relationship breaks down)
[Substitution effects, saturation, regime shifts, seasonality]

## How chat / report / playbooks use this
[The downstream consumption pattern]
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
- `traverse_causes` — walk the causal graph from `from:` metric to `to:` metric, rendering each `metric_relationship` along the path
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
