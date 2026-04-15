# gobiq-knowledge

The single source of truth for GoBIQ's analytical knowledge — consumed by both **GoBIQ chat** and **GoBIQ report**.

## Why this repo exists

Before this repo, GoBIQ chat held its knowledge in `backend/app/ai/knowledge/` and the report system held a parallel set of analytical playbooks elsewhere. Same domain (Indian quick-commerce analytics — Blinkit, Instamart, Zepto), same metrics (OSA, PSL, SOV, market share), but two copies that drifted.

This repo is the merged source. Both apps depend on it as a versioned Python package.

```
                ┌─────────────────────────────────┐
                │   gobiq-knowledge (this repo)   │
                │   typed atomic nodes + loader   │
                └────────────────┬────────────────┘
                                 │  pip install
                ┌────────────────┴────────────────┐
                ▼                                 ▼
        ┌───────────────┐                ┌───────────────┐
        │  GoBIQ chat   │                │ GoBIQ report  │
        │  (1-2 atoms   │                │  (full        │
        │   per turn)   │                │   procedure   │
        │               │                │   walks)      │
        └───────────────┘                └───────────────┘
```

## What's inside

- [`knowledge/`](knowledge/) — all content (typed `_node.yaml` + `content.md` pairs)
- [`src/gobiq_knowledge/`](src/gobiq_knowledge/) — loader + chat assembler + report assembler
- [`tests/`](tests/) — schema validation, reference checks, traversal checks
- [`docs/`](docs/) — architecture, authoring guide, atom-type reference

## Atom types

| Type | Purpose |
|---|---|
| `concept` | Definition + formula of one metric or term (e.g. `osa`, `psl`) |
| `detection` | SQL fragment + threshold that identifies a pattern |
| `threshold` | Value bands tagged to a metric (healthy/warning/critical) |
| `domain` / `topic` | Subject-area knowledge (the existing GoBIQ tree) |
| `procedure` | Typed traversal — decision tree of nodes |
| `recipe` | Q→Action pairs ingested into Milvus for RAG |
| `template` | Chat-layer specs (Layer 0+1 shapes) |
| `output_spec` | Report section specs consumed by the report assembler |
| `global` | Always-loaded content (narration rules, eval rubric) |

See [`docs/content_types.md`](docs/content_types.md) for full details.

## Installation

In your consuming app:

```bash
pip install gobiq-knowledge @ git+ssh://git@github.com/gobblecube/gobiq-knowledge.git@v0.1.0
```

## Usage

### Chat consumer (selective retrieval)

```python
from gobiq_knowledge import load
from gobiq_knowledge.assemblers.chat import assemble_chat_context

graph = load()  # cached singleton at startup

context = assemble_chat_context(
    graph,
    node_id="domains.supply_chain.transfer_issues",
)
```

### Report consumer (full traversal)

```python
from gobiq_knowledge import load
from gobiq_knowledge.assemblers.report import assemble_report

graph = load()
html = assemble_report(
    graph,
    output_spec_id="output_specs.availability_section",
    data_source="path/to/04_analysis.xlsx",
)
```

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for how to add new atoms.

Every PR runs schema validation, reference checks, and traversal checks. PRs cannot merge if any fail.

## Versioning

Semantic versioning, strict:

| Bump | When |
|---|---|
| **Major** | Schema breaks, atom type renamed, loader API changes |
| **Minor** | New atom type, new procedure, new output spec |
| **Patch** | Content edits, threshold tweaks, new individual atoms |

Apps pin a version. No surprise content changes in production.
