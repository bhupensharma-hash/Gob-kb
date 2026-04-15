# Changelog

All notable changes to `gobiq-knowledge` are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - TBD

### Added (additive — no breaking changes)

First-class handling of metric dependencies and causal chains.

#### New atom type: `metric_relationship`

Captures the causal link between two metrics — direction, mechanism, elasticity,
confidence, and caveats. Lives at `knowledge/metric_relationships/{name}/`.

Required `_node.yaml` fields: `source_metric`, `target_metric`, `direction`,
`mechanism_short`. Optional: `elasticity`, `formula`, `confidence`, `caveats`.

Example: [`metric_relationships/osa_drives_psl`](knowledge/metric_relationships/osa_drives_psl/) — documents how OSA drops drive PSL, with elasticity (`₹{daily_demand × price × 0.01} per 1pp drop`), mechanism, and caveats (substitution, demand suppression, festival amplification).

#### New relation types

More precise than the generic `feeds_into`:

- `derives_from` — metric X is mathematically computed from metric Y
- `causes` — metric X's change drives metric Y's change (causal mechanism)
- `correlates_with` — metrics X and Y move together statistically (no causal claim)
- `inverse_of` — when X goes up, Y goes down (and vice versa)

Existing atoms updated: `metrics.osa` and `metrics.psl` now use `causes`/`triggered_by` (instead of `feeds_into`) and link to `metric_relationships.osa_drives_psl`.

#### New traversal step type: `traverse_causes`

Walks the causal graph from a `from:` metric to a `to:` metric (or all reachable nodes if `to:` omitted), rendering each `metric_relationship` along the path.

The example playbook `playbooks.availability_diagnosis` now ends with:

```yaml
- step: traverse_causes
  from: metrics.osa
  to: metrics.psl
  render_each_link: true
```

This means every report assembled from `report_sections.availability_section` now includes a "what it costs" paragraph explaining the OSA→PSL elasticity, automatically.

#### New optional fields on metrics

- `formula:` — explicit math when applicable
- `derives_from:` — list of `{metric, role}` for input metrics

Populated in `metrics.psl` (formula only; `derives_from` commented out pending creation of `metrics.forecast_demand`, `metrics.inventory`, `metrics.price` atoms during Phase 0).

### Why

Real metrics have causal influence (OSA → PSL → market share). The 0.2.0 schema only had a generic `feeds_into` edge that lost direction, mechanism, and elasticity. With `metric_relationship` atoms + typed `causes` edges + `traverse_causes` step, playbooks can now compose causal narratives from a single graph — chat answers questions like "how much PSL recovery if I fix OSA?" with real elasticity numbers; reports include the impact paragraph automatically.

## [0.2.0]

### Changed (BREAKING — schema/atom-type renames; no consumers in production yet)

Adopted the "Option B" taxonomy: atom-type names now match the language analysts already use, fixing the engineer-jargon names from 0.1.0.

| Old name (0.1.0) | New name (0.2.0) | Folder |
|---|---|---|
| `concept` | `metric` | `knowledge/concepts/` → `knowledge/metrics/` |
| `threshold` | `benchmark` | `knowledge/thresholds/` → `knowledge/benchmarks/` |
| `detection` | `diagnostic` | `knowledge/detections/` → `knowledge/diagnostics/` |
| `procedure` | `playbook` | `knowledge/procedures/` → `knowledge/playbooks/` |
| `output_spec` | `report_section` | `knowledge/output_specs/` → `knowledge/report_sections/` |
| `template` | `chat_template` | `knowledge/templates/` → `knowledge/chat_templates/` |

Traversal step types renamed: `run_detection` → `run_diagnostic`, `call_procedure` → `call_playbook`. Relation `uses_threshold` → `uses_benchmark`.

Public Python API renamed: `assemble_report(graph, output_spec_id=...)` → `assemble_report(graph, report_section_id=...)`.

## [0.1.0] - initial scaffold

### Added
- Initial repo scaffolding
- Schema definition (`knowledge/_schema.yaml`) covering atom types
- Loader (`src/gobiq_knowledge/loader.py`) ported from GoBIQ
- Chat assembler (`src/gobiq_knowledge/assemblers/chat.py`)
- Report assembler skeleton (`src/gobiq_knowledge/assemblers/report.py`)
- Example atoms across all atom types
- Schema, reference, and traversal validators in `tests/`
- CI workflow (`.github/workflows/validate.yml`)
