# metric_relationships/

First-class atoms that capture **causal links between metrics** — direction,
mechanism, elasticity, confidence.

## When to create one

Create a `metric_relationship` atom when the link between two metrics has
substance worth reusing:

- **A non-trivial elasticity** that downstream playbooks should quote
- **A mechanism** (not just statistical correlation) worth documenting
- **Caveats** about when the relationship breaks down (substitution,
  saturation, regime shifts)
- **Multiple consumers** — used in several playbooks or reports

If the relationship is obvious and used in only one place, just use a
`related: [{relation: causes}]` edge between the two metric atoms with a
one-line label. Don't proliferate atoms.

## Folder shape

```
knowledge/metric_relationships/{name}/
├── _node.yaml      ← source_metric, target_metric, direction,
│                     mechanism_short, formula, elasticity, confidence, caveats
└── content.md      ← Mechanism in detail, elasticity worked example,
                      caveats explained, how chat/report/playbooks use it
```

## Required `_node.yaml` fields (in addition to the standard ones)

| Field | Purpose |
|---|---|
| `source_metric` | Atom ID of the metric whose change drives the change |
| `target_metric` | Atom ID of the metric being driven |
| `direction` | One of: `increase_causes_increase`, `decrease_causes_increase`, `decrease_causes_decrease`, `increase_causes_decrease` |
| `mechanism_short` | One-sentence description of WHY the link exists |
| `elasticity` | Quantitative rule of thumb (formula or descriptive) |
| `confidence` | One of: `high`, `medium`, `low` |
| `formula` | Optional — explicit math when applicable |
| `caveats` | Optional list — when the relationship breaks down |

## Example

See [`osa_drives_psl/`](osa_drives_psl/) — the canonical example.

## How it's consumed

- **Chat:** planner picks this atom when the user asks about quantifying
  impact between two metrics. The assembler renders the mechanism + elasticity.
- **Report:** playbooks include `render` steps pointing to relationship atoms
  after diagnostics, to translate "what's wrong" into "what it costs".
- **Playbooks:** the `traverse_causes` step walks the causal graph
  (chain of `metric_relationship` atoms) from a source metric to a target,
  rendering each link.
