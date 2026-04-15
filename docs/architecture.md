# Architecture

## One repo, two consumers

```
                   ┌─────────────────────────────────────┐
                   │   gobiq-knowledge (this repo)       │
                   │                                     │
                   │   knowledge/  (typed atomic nodes)  │
                   │   src/        (loader + assemblers) │
                   │   tests/      (CI guardrails)       │
                   └────────────────┬────────────────────┘
                                    │  pip install
                                    │  gobiq-knowledge==X.Y.Z
                ┌───────────────────┴───────────────────┐
                ▼                                       ▼
       ┌────────────────────┐                ┌──────────────────────┐
       │  GoBIQ chat        │                │  GoBIQ report        │
       │                    │                │                      │
       │  uses chat         │                │  uses report         │
       │  assembler         │                │  assembler           │
       │                    │                │                      │
       │  depth-1 retrieval │                │  full procedure      │
       │  per turn          │                │  walks → HTML/PDF    │
       └────────────────────┘                └──────────────────────┘
```

Both consumers read the **same nodes**. They differ only in **how much of the
graph they walk per call**.

## Storage model

Every piece of knowledge is a folder with two files:

```
knowledge/{type}/{id}/
├── _node.yaml      ← typed metadata (parent, related, primitives, etc.)
└── content.md      ← the actual knowledge
```

The `_node.yaml` is machine-validated. Schema lives in [`knowledge/_schema.yaml`](../knowledge/_schema.yaml).

## Atom types

See [`content_types.md`](content_types.md) for the full catalog.

The key distinction:

- **Concept / detection / threshold** atoms hold *what something is* (definitions, formulas, SQL, bands)
- **Procedure** atoms hold *how to diagnose* (typed traversals that reference the above)
- **Output_spec** atoms hold *how to render* (which procedures compose into which report sections, with what CSS)
- **Domain / topic** atoms are the existing GoBIQ subject-area tree (overview content + planner exposure)
- **Recipe** atoms are RAG-indexed Q→Action pairs for fuzzy retrieval

## Relations

Atoms link via typed edges in `_node.yaml`'s `related:` list:

```yaml
related:
  - id: "concepts.psl"
    relation: feeds_into
    label: "OSA gaps drive PSL"
```

Relation types: `next_action`, `root_cause`, `cross_check`, `uses_template`,
`uses_threshold`, `feeds_into`, `triggered_by`, `composes`, `rendered_by`.

Relations are bidirectional — if A says `related: B`, B should say `related: A`.
The reference checker enforces this.

## Loading

```python
from gobiq_knowledge import load

graph = load()  # cached singleton
```

The loader walks `knowledge/`, parses every `_node.yaml`, validates references,
and returns a `KnowledgeGraph` with O(1) `get_node(id)` access.

## Chat assembly

```python
from gobiq_knowledge.assemblers.chat import assemble_chat_context

ctx = assemble_chat_context(graph, node_id="domains.supply_chain.transfer_issues")
```

Returns a context blob with: global narration rules + parent chain + node
content + related summary. Drop into the LLM prompt as-is.

## Report assembly

```python
from gobiq_knowledge.assemblers.report import assemble_report

report = assemble_report(
    graph,
    output_spec_id="output_specs.availability_section",
    data_fetcher=my_data_fetcher,  # callback that runs SQL / reads Excel
)
html = report.to_html()
```

The assembler walks the output_spec's referenced procedures end-to-end. The
consumer supplies a `data_fetcher` callback for steps that need real data
(`run_detection`, `fetch_data`).

## Why the consumer owns data fetching

This package owns **knowledge**, not **data**. The consumer (chat backend or
report backend) knows its own Snowflake credentials, query engine, and Excel
loader. The assembler stays portable.

## Migration phases

See [`/CHANGELOG.md`](../CHANGELOG.md) for what's done. Migration order:

1. **Phase 0** — Lift GoBIQ's existing `domains/`, `recipes/`, `templates/`,
   `global/` content into this repo. Refactor GoBIQ chat to import from the
   package. Behavior-preserving.
2. **Phase 1** — Add new atom types in schema (done). Author starter atoms (done).
3. **Phase 2** — Build the report assembler (skeleton done).
4. **Phase 3** — Migrate strategy-agent-core's `availability_deep_dive.md`
   into atomic form. Validate output equivalence.
5. **Phase 4** — One domain per cycle: supply_chain → market_share → visibility → pricing.
6. **Phase 5** — Decommission strategy-agent-core's knowledge folder.
