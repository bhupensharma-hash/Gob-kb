# Changelog

All notable changes to `gobiq-knowledge` are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - TBD

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
| `recipe` / `domain` / `topic` / `global` / `category` | (unchanged) | (unchanged) |

Traversal step types renamed:

| Old | New |
|---|---|
| `run_detection` | `run_diagnostic` |
| `call_procedure` | `call_playbook` |

Public Python API renamed:
- `assemble_report(graph, output_spec_id=...)` → `assemble_report(graph, report_section_id=...)`
- `AssembledReport.output_spec_id` → `AssembledReport.report_section_id`

### Why

The 0.1.0 names were generic engineer jargon (`output_spec`, `procedure`, `concept`) that didn't match the domain language analysts already use ("benchmark", "playbook", "metric", "report section"). Renaming now is cheap (no production consumers); renaming after Phase 0 migration would be a major version bump that breaks every consuming app.

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
